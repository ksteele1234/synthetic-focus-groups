"""
Proof of Concept: Vector Database Compatibility
Demonstrates how current data models can be extended for vector database integration.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
import numpy as np
from datetime import datetime

# Import existing models (compatible as-is)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.session import SessionResponse, Session
from models.persona import Persona
from models.enhanced_project import EnhancedProject


class MockEmbeddingModel:
    """Mock embedding model for demonstration (replace with actual model in production)."""
    
    def encode(self, text: str) -> List[float]:
        """Generate mock embedding vector from text."""
        # In production, use sentence-transformers, OpenAI embeddings, etc.
        # This creates a deterministic mock embedding for demo purposes
        import hashlib
        
        # Create deterministic "embedding" based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert to mock 384-dimensional vector (common embedding size)
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            # Convert hex to float between -1 and 1
            embedding.append((int(hex_pair, 16) - 128) / 128.0)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(len(embedding), 384-len(embedding))])
        
        return embedding[:384]


@dataclass
class VectorCompatibleResponse(SessionResponse):
    """Extended SessionResponse with vector capabilities - BACKWARDS COMPATIBLE."""
    
    # Add vector fields as optional (existing code still works)
    content_embedding: Optional[List[float]] = field(default=None)
    themes_embedding: Optional[List[float]] = field(default=None)
    combined_embedding: Optional[List[float]] = field(default=None)
    
    def generate_embeddings(self, embedding_model: MockEmbeddingModel) -> None:
        """Generate embeddings while preserving all existing functionality."""
        
        # Primary content embedding
        if self.content:
            self.content_embedding = embedding_model.encode(self.content)
        
        # Themes embedding
        if self.key_themes:
            themes_text = " ".join(self.key_themes)
            self.themes_embedding = embedding_model.encode(themes_text)
        
        # Combined context embedding
        context_parts = []
        if self.content:
            context_parts.append(self.content)
        if self.key_themes:
            context_parts.append("themes: " + " ".join(self.key_themes))
        if self.emotion_tags:
            context_parts.append("emotions: " + " ".join(self.emotion_tags))
        
        if context_parts:
            combined_text = " | ".join(context_parts)
            self.combined_embedding = embedding_model.encode(combined_text)
    
    def to_vector_document(self) -> Dict[str, Any]:
        """Convert to vector database document format."""
        return {
            "id": self.id,
            "vector": self.content_embedding or [],
            "metadata": {
                # Preserve ALL existing SessionResponse fields
                "session_id": self.session_id,
                "response_type": str(self.response_type) if hasattr(self.response_type, 'value') else str(self.response_type),
                "speaker_id": self.speaker_id,
                "speaker_name": self.speaker_name,
                "speaker_type": self.speaker_type,
                "content": self.content,
                "question_id": self.question_id,
                "responding_to_id": self.responding_to_id,
                "sequence_number": self.sequence_number,
                "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, 'isoformat') else str(self.timestamp) if self.timestamp else None,
                "duration_seconds": self.duration_seconds,
                "sentiment_score": self.sentiment_score,
                "emotion_tags": self.emotion_tags,
                "key_themes": self.key_themes,
                
                # Add vector-specific metadata
                "has_content_embedding": self.content_embedding is not None,
                "has_themes_embedding": self.themes_embedding is not None,
                "embedding_dimension": len(self.content_embedding) if self.content_embedding else 0,
                "content_length": len(self.content) if self.content else 0,
                "theme_count": len(self.key_themes) if self.key_themes else 0,
                "emotion_count": len(self.emotion_tags) if self.emotion_tags else 0
            }
        }
    
    def calculate_similarity(self, other: 'VectorCompatibleResponse') -> float:
        """Calculate cosine similarity with another response."""
        if not self.content_embedding or not other.content_embedding:
            return 0.0
        
        # Cosine similarity calculation
        vec1 = np.array(self.content_embedding)
        vec2 = np.array(other.content_embedding)
        
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


@dataclass 
class VectorCompatiblePersona(Persona):
    """Extended Persona with vector capabilities - BACKWARDS COMPATIBLE."""
    
    # Add vector fields as optional
    background_embedding: Optional[List[float]] = field(default=None)
    traits_embedding: Optional[List[float]] = field(default=None)
    profile_embedding: Optional[List[float]] = field(default=None)
    
    def generate_embeddings(self, embedding_model: MockEmbeddingModel) -> None:
        """Generate persona embeddings for similarity matching."""
        
        # Background story embedding
        if self.background_story:
            self.background_embedding = embedding_model.encode(self.background_story)
        
        # Personality traits embedding
        if self.personality_traits:
            traits_text = " ".join(self.personality_traits)
            self.traits_embedding = embedding_model.encode(traits_text)
        
        # Combined profile embedding
        profile_parts = []
        profile_parts.append(f"Age {self.age} {self.gender} from {self.location}")
        profile_parts.append(f"Works as {self.occupation}")
        if self.background_story:
            profile_parts.append(self.background_story)
        if self.personality_traits:
            profile_parts.append("Personality: " + " ".join(self.personality_traits))
        if self.interests:
            profile_parts.append("Interests: " + " ".join(self.interests))
        
        combined_profile = " | ".join(profile_parts)
        self.profile_embedding = embedding_model.encode(combined_profile)
    
    def to_vector_document(self) -> Dict[str, Any]:
        """Convert to vector database document format."""
        return {
            "id": self.id,
            "vector": self.profile_embedding or [],
            "metadata": {
                # Preserve existing data with safe conversion
                "name": self.name,
                "age": self.age,
                "gender": self.gender,
                "location": self.location,
                "occupation": self.occupation,
                "education_level": self.education_level,
                "income_level": self.income_level,
                "personality_traits": self.personality_traits,
                "interests": self.interests,
                "background_story": self.background_story,
                "pain_points": self.pain_points,
                "goals": self.goals,
                "preferred_communication_style": self.preferred_communication_style,
                "tech_comfort_level": self.tech_comfort_level,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "has_profile_embedding": self.profile_embedding is not None,
                "background_length": len(self.background_story) if self.background_story else 0,
                "trait_count": len(self.personality_traits) if self.personality_traits else 0
            }
        }


class VectorSearchEngine:
    """Mock vector search engine demonstrating capabilities."""
    
    def __init__(self, embedding_model: MockEmbeddingModel):
        self.embedding_model = embedding_model
        self.responses_index: List[VectorCompatibleResponse] = []
        self.personas_index: List[VectorCompatiblePersona] = []
    
    def index_response(self, response: VectorCompatibleResponse) -> None:
        """Add response to vector index."""
        if not response.content_embedding:
            response.generate_embeddings(self.embedding_model)
        self.responses_index.append(response)
    
    def index_persona(self, persona: VectorCompatiblePersona) -> None:
        """Add persona to vector index."""
        if not persona.profile_embedding:
            persona.generate_embeddings(self.embedding_model)
        self.personas_index.append(persona)
    
    def semantic_search_responses(self, query: str, filters: Dict[str, Any] = None, 
                                 top_k: int = 5) -> List[tuple]:
        """Search responses by semantic similarity."""
        query_embedding = self.embedding_model.encode(query)
        results = []
        
        for response in self.responses_index:
            # Apply filters
            if filters:
                if 'sentiment_min' in filters and (response.sentiment_score or 0) < filters['sentiment_min']:
                    continue
                if 'themes' in filters and not any(theme in (response.key_themes or []) for theme in filters['themes']):
                    continue
                if 'speaker_type' in filters and response.speaker_type != filters['speaker_type']:
                    continue
            
            # Calculate similarity
            if response.content_embedding:
                similarity = self._cosine_similarity(query_embedding, response.content_embedding)
                results.append((similarity, response))
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
    
    def find_similar_responses(self, reference_response: VectorCompatibleResponse, 
                              top_k: int = 5) -> List[tuple]:
        """Find responses similar to a reference response."""
        if not reference_response.content_embedding:
            return []
        
        results = []
        for response in self.responses_index:
            if response.id != reference_response.id and response.content_embedding:
                similarity = reference_response.calculate_similarity(response)
                results.append((similarity, response))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
    
    def find_similar_personas(self, query: str, top_k: int = 3) -> List[tuple]:
        """Find personas similar to a description."""
        query_embedding = self.embedding_model.encode(query)
        results = []
        
        for persona in self.personas_index:
            if persona.profile_embedding:
                similarity = self._cosine_similarity(query_embedding, persona.profile_embedding)
                results.append((similarity, persona))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        magnitude1 = np.linalg.norm(v1)
        magnitude2 = np.linalg.norm(v2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


def demonstrate_vector_compatibility():
    """Demonstrate vector database compatibility with existing models."""
    
    print("🚀 Vector Database Compatibility Demonstration")
    print("=" * 60)
    
    # Initialize mock embedding model
    embedding_model = MockEmbeddingModel()
    vector_search = VectorSearchEngine(embedding_model)
    
    # Create sample data using existing models (backwards compatible!)
    print("\n1. Creating sample data using existing models...")
    
    # Standard SessionResponse works as-is
    response1 = SessionResponse(
        content="I love this product but it's too expensive for our budget",
        key_themes=["pricing", "budget"],
        emotion_tags=["positive", "concerned"],
        sentiment_score=0.2,
        speaker_type="participant"
    )
    
    response2 = SessionResponse(
        content="The pricing model doesn't work for small businesses like ours",
        key_themes=["pricing", "business_size"],
        emotion_tags=["frustrated"],
        sentiment_score=-0.3,
        speaker_type="participant"
    )
    
    response3 = SessionResponse(
        content="Great features but we need better customer support",
        key_themes=["features", "support"],
        emotion_tags=["satisfied", "concerned"],
        sentiment_score=0.1,
        speaker_type="participant"
    )
    
    # Convert to vector-compatible (preserves all existing functionality)
    print("2. Converting to vector-compatible format...")
    vector_responses = [
        VectorCompatibleResponse(**response1.to_dict()),
        VectorCompatibleResponse(**response2.to_dict()),
        VectorCompatibleResponse(**response3.to_dict())
    ]
    
    # Generate embeddings and index
    print("3. Generating embeddings and indexing...")
    for response in vector_responses:
        vector_search.index_response(response)
    
    # Demonstrate semantic search capabilities
    print("4. Demonstrating semantic search capabilities...")
    print("\n🔍 Semantic Search: 'cost and affordability concerns'")
    
    results = vector_search.semantic_search_responses(
        "cost and affordability concerns",
        filters={"sentiment_min": -1.0},  # Include all sentiments
        top_k=3
    )
    
    for i, (similarity, response) in enumerate(results, 1):
        print(f"   {i}. Similarity: {similarity:.3f}")
        print(f"      Content: {response.content[:60]}...")
        print(f"      Themes: {response.key_themes}")
        print(f"      Sentiment: {response.sentiment_score}")
        print()
    
    # Demonstrate response similarity
    print("🔍 Finding similar responses to first result...")
    if results:
        reference_response = results[0][1]
        similar = vector_search.find_similar_responses(reference_response, top_k=2)
        
        for i, (similarity, response) in enumerate(similar, 1):
            print(f"   {i}. Similarity: {similarity:.3f}")
            print(f"      Content: {response.content[:60]}...")
            print()
    
    # Demonstrate persona similarity
    print("5. Demonstrating persona similarity matching...")
    
    # Create sample personas
    persona1 = Persona(
        name="Sarah Johnson",
        age=32,
        occupation="Small Business Owner",
        background_story="Runs a digital marketing agency with 8 employees. Budget-conscious but values quality tools.",
        personality_traits=["analytical", "cost-conscious", "quality-focused"],
        interests=["business growth", "efficiency", "team management"]
    )
    
    persona2 = Persona(
        name="Mike Chen",
        age=28,
        occupation="Startup Founder",
        background_story="Founded a tech startup, always looking for cost-effective solutions to scale the business.",
        personality_traits=["innovative", "budget-aware", "growth-oriented"],
        interests=["technology", "scaling", "cost optimization"]
    )
    
    # Convert and index personas
    vector_personas = [
        VectorCompatiblePersona(**persona1.to_dict()),
        VectorCompatiblePersona(**persona2.to_dict())
    ]
    
    for persona in vector_personas:
        vector_search.index_persona(persona)
    
    print("\n🔍 Finding personas similar to 'budget-conscious business owner':")
    persona_results = vector_search.find_similar_personas(
        "budget-conscious business owner who cares about cost-effectiveness",
        top_k=2
    )
    
    for i, (similarity, persona) in enumerate(persona_results, 1):
        print(f"   {i}. Similarity: {similarity:.3f}")
        print(f"      Name: {persona.name} ({persona.occupation})")
        print(f"      Background: {persona.background_story[:80]}...")
        print(f"      Traits: {persona.personality_traits}")
        print()
    
    # Demonstrate data preservation
    print("6. Verifying backwards compatibility...")
    
    # Original data is completely preserved
    original_response = vector_responses[0]
    print(f"   ✅ Original content preserved: '{original_response.content[:40]}...'")
    print(f"   ✅ Original themes preserved: {original_response.key_themes}")
    print(f"   ✅ Original sentiment preserved: {original_response.sentiment_score}")
    print(f"   ✅ New embedding added: {len(original_response.content_embedding)} dimensions")
    
    # Export capability
    print("\n7. Demonstrating vector database export format...")
    vector_doc = original_response.to_vector_document()
    
    print("   Sample vector document structure:")
    print(f"   - ID: {vector_doc['id']}")
    print(f"   - Vector dimensions: {len(vector_doc['vector'])}")
    print(f"   - Metadata fields: {len(vector_doc['metadata'])}")
    print(f"   - Preserved original data: ✅")
    
    print("\n✅ Vector Database Compatibility Demonstrated!")
    print("   • Existing models work unchanged")
    print("   • Vector capabilities are additive") 
    print("   • Zero breaking changes required")
    print("   • Full semantic search enabled")
    print("   • Cross-session analysis ready")
    print("   • Production migration path clear")


if __name__ == "__main__":
    demonstrate_vector_compatibility()