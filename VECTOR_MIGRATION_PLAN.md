# Vector Database Migration Plan

This document outlines a practical migration plan to add vector database capabilities to the synthetic focus groups system while maintaining full backward compatibility.

## Overview

The proof-of-concept demonstrates that our existing data models can be seamlessly extended with vector database capabilities without breaking existing functionality. This migration plan provides a step-by-step approach to implement production-ready vector capabilities.

## Migration Phases

### Phase 1: Infrastructure Setup (Week 1-2)

#### 1.1 Dependencies and Environment
```bash
# Add to requirements.txt
sentence-transformers>=2.2.2  # For embeddings
pinecone-client>=2.2.0        # Vector database (option 1)
# OR
chromadb>=0.4.0               # Vector database (option 2)
# OR 
weaviate-client>=3.20.0       # Vector database (option 3)

faiss-cpu>=1.7.4              # For local similarity search (optional)
numpy>=1.21.0                 # Already present, verify version
```

#### 1.2 Configuration
```python
# src/config/vector_config.py
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class VectorConfig:
    """Vector database configuration."""
    
    # Embedding model settings
    embedding_model: str = "all-MiniLM-L6-v2"  # Fast, good quality
    embedding_dimension: int = 384
    
    # Vector database settings
    provider: str = "pinecone"  # pinecone, chroma, weaviate
    index_name: str = "synthetic-focus-groups"
    
    # Pinecone specific
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    
    # Performance settings
    batch_size: int = 100
    similarity_threshold: float = 0.7
    max_results: int = 50
    
    def __post_init__(self):
        # Load from environment if available
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY", self.pinecone_api_key)
```

### Phase 2: Core Vector Extensions (Week 3-4)

#### 2.1 Embedding Service
```python
# src/services/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from config.vector_config import VectorConfig

class EmbeddingService:
    """Service for generating embeddings from text content."""
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.model = SentenceTransformer(config.embedding_model)
    
    def encode_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            return [0.0] * self.config.embedding_dimension
        
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        clean_texts = [text if text and text.strip() else "" for text in texts]
        embeddings = self.model.encode(clean_texts)
        return embeddings.tolist()
```

#### 2.2 Vector-Compatible Models
```python
# src/models/vector_models.py
from models.session import SessionResponse
from models.persona import Persona
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class VectorSessionResponse(SessionResponse):
    """SessionResponse with vector capabilities."""
    
    # Vector fields (optional for backward compatibility)
    content_embedding: Optional[List[float]] = field(default=None)
    themes_embedding: Optional[List[float]] = field(default=None)
    combined_embedding: Optional[List[float]] = field(default=None)
    
    # Metadata for vector operations
    embedding_model: Optional[str] = field(default=None)
    embedding_timestamp: Optional[str] = field(default=None)
    
    def has_embeddings(self) -> bool:
        """Check if response has embeddings."""
        return self.content_embedding is not None
    
    def to_vector_document(self) -> Dict[str, Any]:
        """Convert to vector database document."""
        return {
            "id": self.id,
            "vector": self.content_embedding or [],
            "metadata": {
                # All original SessionResponse fields
                "session_id": self.session_id,
                "content": self.content,
                "speaker_type": self.speaker_type,
                "sentiment_score": self.sentiment_score,
                "key_themes": self.key_themes,
                "emotion_tags": self.emotion_tags,
                # Add vector metadata
                "has_embeddings": self.has_embeddings(),
                "embedding_model": self.embedding_model,
                "content_length": len(self.content) if self.content else 0,
                "theme_count": len(self.key_themes) if self.key_themes else 0
            }
        }

@dataclass
class VectorPersona(Persona):
    """Persona with vector capabilities."""
    
    profile_embedding: Optional[List[float]] = field(default=None)
    background_embedding: Optional[List[float]] = field(default=None)
    traits_embedding: Optional[List[float]] = field(default=None)
    
    embedding_model: Optional[str] = field(default=None)
    embedding_timestamp: Optional[str] = field(default=None)
    
    def to_vector_document(self) -> Dict[str, Any]:
        """Convert to vector database document."""
        return {
            "id": self.id,
            "vector": self.profile_embedding or [],
            "metadata": {
                "name": self.name,
                "occupation": self.occupation,
                "background_story": self.background_story,
                "personality_traits": self.personality_traits,
                "has_embeddings": self.profile_embedding is not None,
                "embedding_model": self.embedding_model
            }
        }
```

#### 2.3 Vector Database Service
```python
# src/services/vector_service.py
from typing import List, Dict, Any, Tuple, Optional
import pinecone
from config.vector_config import VectorConfig
from services.embedding_service import EmbeddingService

class VectorService:
    """Service for vector database operations."""
    
    def __init__(self, config: VectorConfig):
        self.config = config
        self.embedding_service = EmbeddingService(config)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize vector database connection."""
        if self.config.provider == "pinecone":
            pinecone.init(
                api_key=self.config.pinecone_api_key,
                environment=self.config.pinecone_environment
            )
            
            # Create index if it doesn't exist
            if self.config.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.config.index_name,
                    dimension=self.config.embedding_dimension,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(self.config.index_name)
    
    def index_response(self, response: 'VectorSessionResponse') -> bool:
        """Index a response in the vector database."""
        if not response.has_embeddings():
            # Generate embeddings if missing
            response.content_embedding = self.embedding_service.encode_single(response.content)
            response.embedding_model = self.config.embedding_model
        
        vector_doc = response.to_vector_document()
        
        try:
            self.index.upsert(vectors=[
                (vector_doc["id"], vector_doc["vector"], vector_doc["metadata"])
            ])
            return True
        except Exception as e:
            print(f"Error indexing response: {e}")
            return False
    
    def semantic_search(self, query: str, filters: Dict[str, Any] = None, 
                       top_k: int = 10) -> List[Tuple[float, Dict[str, Any]]]:
        """Search for similar responses using semantic similarity."""
        query_embedding = self.embedding_service.encode_single(query)
        
        try:
            results = self.index.query(
                vector=query_embedding,
                filter=filters,
                top_k=top_k,
                include_metadata=True
            )
            
            return [(match.score, match.metadata) for match in results.matches]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
```

### Phase 3: Gradual Integration (Week 5-6)

#### 3.1 Update Session Management
```python
# src/managers/session_manager.py (additions)

from models.vector_models import VectorSessionResponse
from services.vector_service import VectorService

class SessionManager:
    def __init__(self):
        # Existing initialization
        self.vector_service = None  # Initialize only if vector features enabled
    
    def enable_vector_features(self, vector_config: VectorConfig):
        """Enable vector database features."""
        try:
            self.vector_service = VectorService(vector_config)
            print("✅ Vector features enabled")
        except Exception as e:
            print(f"❌ Could not enable vector features: {e}")
            self.vector_service = None
    
    def add_response(self, session_id: str, response_data: dict) -> SessionResponse:
        """Add response with optional vector indexing."""
        # Create standard response first (backward compatible)
        response = SessionResponse(**response_data)
        
        # Add to session as usual
        session = self.get_session(session_id)
        session.add_response(response)
        
        # If vector features enabled, also index
        if self.vector_service:
            vector_response = VectorSessionResponse(**response.to_dict())
            self.vector_service.index_response(vector_response)
        
        return response
    
    def search_similar_responses(self, query: str, session_id: str = None) -> List[dict]:
        """Search for similar responses across sessions."""
        if not self.vector_service:
            return []  # Graceful degradation
        
        filters = {}
        if session_id:
            filters["session_id"] = session_id
        
        return self.vector_service.semantic_search(query, filters)
```

#### 3.2 Add CLI Commands
```python
# cli.py (additions)

import click
from config.vector_config import VectorConfig

@cli.group()
def vector():
    """Vector database operations."""
    pass

@vector.command()
@click.option('--provider', default='pinecone', help='Vector database provider')
@click.option('--reindex', is_flag=True, help='Reindex existing data')
def setup(provider, reindex):
    """Setup vector database."""
    config = VectorConfig(provider=provider)
    
    try:
        from services.vector_service import VectorService
        vector_service = VectorService(config)
        click.echo(f"✅ Vector database '{provider}' setup complete")
        
        if reindex:
            click.echo("🔄 Reindexing existing data...")
            # Reindex logic here
            click.echo("✅ Reindexing complete")
            
    except Exception as e:
        click.echo(f"❌ Setup failed: {e}")

@vector.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum results')
@click.option('--session-id', help='Limit to specific session')
def search(query, limit, session_id):
    """Search responses by semantic similarity."""
    try:
        config = VectorConfig()
        vector_service = VectorService(config)
        
        filters = {}
        if session_id:
            filters["session_id"] = session_id
        
        results = vector_service.semantic_search(query, filters, top_k=limit)
        
        click.echo(f"\n🔍 Found {len(results)} similar responses for: '{query}'\n")
        
        for i, (score, metadata) in enumerate(results, 1):
            click.echo(f"{i}. Similarity: {score:.3f}")
            click.echo(f"   Content: {metadata.get('content', '')[:80]}...")
            click.echo(f"   Session: {metadata.get('session_id', 'Unknown')}")
            click.echo(f"   Themes: {metadata.get('key_themes', [])}")
            click.echo()
            
    except Exception as e:
        click.echo(f"❌ Search failed: {e}")
```

### Phase 4: Advanced Features (Week 7-8)

#### 4.1 Cross-Session Analytics
```python
# src/analytics/vector_analytics.py
from typing import List, Dict, Any, Tuple
from services.vector_service import VectorService

class VectorAnalytics:
    """Advanced analytics using vector similarities."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
    
    def find_recurring_themes(self, sessions: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find themes that recur across multiple sessions."""
        themes = {}
        
        for session_id in sessions:
            # Get all responses from session
            responses = self.vector_service.semantic_search(
                query="",  # Empty query to get all
                filters={"session_id": session_id}
            )
            
            # Extract and cluster themes
            for score, metadata in responses:
                for theme in metadata.get('key_themes', []):
                    if theme not in themes:
                        themes[theme] = {
                            'sessions': set(),
                            'responses': [],
                            'avg_sentiment': 0
                        }
                    
                    themes[theme]['sessions'].add(session_id)
                    themes[theme]['responses'].append(metadata)
        
        # Return themes appearing in multiple sessions
        recurring = []
        for theme, data in themes.items():
            if len(data['sessions']) >= 2:  # Appears in 2+ sessions
                recurring.append({
                    'theme': theme,
                    'session_count': len(data['sessions']),
                    'response_count': len(data['responses']),
                    'sessions': list(data['sessions'])
                })
        
        return sorted(recurring, key=lambda x: x['session_count'], reverse=True)
    
    def persona_similarity_analysis(self, personas: List[str]) -> Dict[str, List[Tuple[str, float]]]:
        """Find similar personas across different sessions."""
        similarities = {}
        
        # Get embeddings for all personas
        persona_embeddings = {}
        for persona_id in personas:
            # Query for persona data
            results = self.vector_service.semantic_search(
                query="",
                filters={"speaker_id": persona_id}
            )
            if results:
                persona_embeddings[persona_id] = results[0][1]  # Get first result
        
        # Calculate similarities
        for p1 in personas:
            similarities[p1] = []
            for p2 in personas:
                if p1 != p2 and p1 in persona_embeddings and p2 in persona_embeddings:
                    # Calculate cosine similarity between personas
                    similarity = self._calculate_similarity(
                        persona_embeddings[p1], 
                        persona_embeddings[p2]
                    )
                    similarities[p1].append((p2, similarity))
            
            # Sort by similarity
            similarities[p1].sort(key=lambda x: x[1], reverse=True)
        
        return similarities
```

#### 4.2 Web UI Integration
```python
# app.py (additions to Streamlit app)

import streamlit as st
from services.vector_service import VectorService
from analytics.vector_analytics import VectorAnalytics

def show_vector_features():
    """Display vector database features in the web UI."""
    
    st.subheader("🔍 Semantic Search & Analysis")
    
    # Enable vector features if not already enabled
    if 'vector_service' not in st.session_state:
        if st.button("🚀 Enable Vector Features"):
            try:
                config = VectorConfig()
                st.session_state.vector_service = VectorService(config)
                st.success("Vector features enabled!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Could not enable vector features: {e}")
                return
    
    if 'vector_service' not in st.session_state:
        st.info("Vector features not enabled. Click the button above to enable semantic search.")
        return
    
    # Semantic search interface
    st.write("### Semantic Response Search")
    search_query = st.text_input("Search for responses by meaning:")
    
    if search_query:
        results = st.session_state.vector_service.semantic_search(
            search_query, 
            top_k=10
        )
        
        if results:
            st.write(f"Found {len(results)} similar responses:")
            
            for i, (score, metadata) in enumerate(results):
                with st.expander(f"Match {i+1} (Similarity: {score:.3f})"):
                    st.write(f"**Content:** {metadata.get('content', '')}")
                    st.write(f"**Session:** {metadata.get('session_id', 'Unknown')}")
                    st.write(f"**Themes:** {metadata.get('key_themes', [])}")
                    st.write(f"**Sentiment:** {metadata.get('sentiment_score', 'N/A')}")
        else:
            st.write("No similar responses found.")
    
    # Cross-session analytics
    st.write("### Cross-Session Theme Analysis")
    
    if st.button("Analyze Recurring Themes"):
        analytics = VectorAnalytics(st.session_state.vector_service)
        
        # Get all sessions
        session_ids = [session.id for session in st.session_state.get('sessions', [])]
        
        if len(session_ids) >= 2:
            recurring_themes = analytics.find_recurring_themes(session_ids)
            
            if recurring_themes:
                st.write("**Themes appearing across multiple sessions:**")
                
                for theme_data in recurring_themes:
                    st.write(f"- **{theme_data['theme']}**: "
                           f"Appears in {theme_data['session_count']} sessions "
                           f"({theme_data['response_count']} responses)")
            else:
                st.write("No recurring themes found across sessions.")
        else:
            st.write("Need at least 2 sessions to analyze recurring themes.")

# Add to main app
def main():
    # ... existing code ...
    
    # Add vector features tab
    tab_vector = st.tabs(["Create Study", "Run Session", "Results", "Exports", "Vector Search"])
    
    with tab_vector[-1]:  # Vector Search tab
        show_vector_features()
```

### Phase 5: Production Optimization (Week 9-10)

#### 5.1 Performance Optimizations
- Implement batch embedding generation
- Add embedding caching
- Optimize vector index structure
- Add connection pooling

#### 5.2 Monitoring and Maintenance
```python
# src/monitoring/vector_monitoring.py
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class VectorMonitoring:
    """Monitor vector database performance and health."""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.metrics = {
            'search_times': [],
            'index_times': [],
            'errors': [],
            'total_searches': 0,
            'total_indexes': 0
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on vector database."""
        start_time = time.time()
        
        try:
            # Test search
            test_results = self.vector_service.semantic_search(
                "test query", 
                top_k=1
            )
            
            search_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'search_time_ms': search_time * 1000,
                'index_size': len(test_results),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'avg_search_time_ms': sum(self.metrics['search_times']) / max(len(self.metrics['search_times']), 1),
            'avg_index_time_ms': sum(self.metrics['index_times']) / max(len(self.metrics['index_times']), 1),
            'total_searches': self.metrics['total_searches'],
            'total_indexes': self.metrics['total_indexes'],
            'error_count': len(self.metrics['errors'])
        }
```

## Deployment Strategy

### Environment Variables
```bash
# .env additions
VECTOR_FEATURES_ENABLED=true
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
VECTOR_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Docker Updates
```dockerfile
# Add to Dockerfile
RUN pip install sentence-transformers pinecone-client
```

### Migration Commands
```bash
# Setup vector database
python -m cli vector setup --provider pinecone

# Reindex existing data
python -m cli vector setup --reindex

# Test vector search
python -m cli vector search "pricing concerns" --limit 5
```

## Benefits After Migration

1. **Semantic Search**: Find relevant responses by meaning, not just keywords
2. **Cross-Session Analysis**: Identify patterns and themes across multiple focus groups
3. **Similar Response Discovery**: Find related feedback automatically
4. **Persona Clustering**: Group similar participant types
5. **Advanced Analytics**: Deeper insights through vector similarity analysis
6. **Better Recommendations**: Suggest relevant questions based on response patterns

## Backward Compatibility Guarantee

- ✅ All existing CLI commands work unchanged
- ✅ All existing data formats remain valid
- ✅ Existing web UI functions normally
- ✅ Vector features are purely additive
- ✅ No breaking changes to APIs
- ✅ Graceful degradation if vector features disabled

## Cost Considerations

- **Pinecone**: ~$70/month for 1M vectors (384 dimensions)
- **OpenAI Embeddings**: Alternative to sentence-transformers (~$0.10/1M tokens)
- **Local Vector DB**: Use ChromaDB or Faiss for free local deployment
- **Compute**: Minimal additional compute for embedding generation

## Success Metrics

- Search relevance improvement: >80% user satisfaction
- Response time: <500ms for semantic searches
- Cross-session insights: Find 3+ recurring themes per analysis
- User adoption: >50% of users try vector search within 30 days
- System reliability: 99.9% uptime with vector features enabled

This migration plan ensures a smooth, risk-free transition to vector-enhanced capabilities while maintaining all existing functionality.