"""
Storage system for Q/A turns - writes JSONL and auto-generates CSV.
"""

import os
import json
import csv
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from models.qa_turn import QATurn, validate_qa_turns


class QAStorage:
    """Handles storage of Q/A turns in JSONL and CSV formats."""
    
    def __init__(self, base_path: str = "data/sessions"):
        """Initialize storage system."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def create_session_folder(self, study_id: str, session_id: str) -> Path:
        """Create folder structure for a session."""
        session_folder = self.base_path / study_id / session_id
        session_folder.mkdir(parents=True, exist_ok=True)
        return session_folder
        
    def save_qa_turns(self, qa_turns: List[QATurn], study_id: str, session_id: str) -> Dict[str, str]:
        """Save Q/A turns to JSONL and CSV formats."""
        
        # Validate all turns first
        errors = validate_qa_turns(qa_turns)
        if errors:
            raise ValueError(f"Schema validation errors: {errors}")
        
        # Create session folder
        session_folder = self.create_session_folder(study_id, session_id)
        
        # Generate filenames with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        jsonl_filename = f"{session_id}_{timestamp}.jsonl"
        csv_filename = f"{session_id}_{timestamp}.csv"
        
        jsonl_path = session_folder / jsonl_filename
        csv_path = session_folder / csv_filename
        
        # Save JSONL
        self._save_jsonl(qa_turns, jsonl_path)
        
        # Save CSV
        self._save_csv(qa_turns, csv_path)
        
        # Create metadata file
        metadata = {
            "study_id": study_id,
            "session_id": session_id,
            "total_turns": len(qa_turns),
            "personas": list(set(turn.persona_id for turn in qa_turns)),
            "rounds": list(set(turn.round_id for turn in qa_turns)),
            "created_at": datetime.now().isoformat(),
            "files": {
                "jsonl": jsonl_filename,
                "csv": csv_filename
            },
            "validation": {
                "schema_errors": 0,
                "validated_at": datetime.now().isoformat()
            }
        }
        
        metadata_path = session_folder / f"{session_id}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "jsonl_path": str(jsonl_path),
            "csv_path": str(csv_path),
            "metadata_path": str(metadata_path),
            "session_folder": str(session_folder)
        }
    
    def _save_jsonl(self, qa_turns: List[QATurn], filepath: Path) -> None:
        """Save Q/A turns as JSONL format."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for turn in qa_turns:
                # Validate each turn before writing
                turn.validate_schema()
                f.write(turn.to_json() + '\n')
    
    def _save_csv(self, qa_turns: List[QATurn], filepath: Path) -> None:
        """Save Q/A turns as CSV format."""
        if not qa_turns:
            return
        
        # Convert to list of dictionaries
        data = [turn.to_dict() for turn in qa_turns]
        
        # Create DataFrame and save
        df = pd.DataFrame(data)
        
        # Reorder columns to match schema
        column_order = [
            'study_id', 'session_id', 'persona_id', 'round_id',
            'question', 'answer', 'follow_up_question', 'follow_up_answer',
            'confidence_0_1', 'tags', 'ts'
        ]
        
        df = df[column_order]
        
        # Convert tags list to string for CSV
        df['tags'] = df['tags'].apply(lambda x: ';'.join(x) if isinstance(x, list) else str(x))
        
        df.to_csv(filepath, index=False, encoding='utf-8')
    
    def load_qa_turns(self, jsonl_path: str) -> List[QATurn]:
        """Load Q/A turns from JSONL file."""
        qa_turns = []
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    turn = QATurn.from_dict(data)
                    turn.validate_schema()  # Ensure loaded data is valid
                    qa_turns.append(turn)
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Error loading line {line_num}: {e}")
        
        return qa_turns
    
    def get_session_files(self, study_id: str, session_id: str) -> Dict[str, List[str]]:
        """Get all files for a session."""
        session_folder = self.base_path / study_id / session_id
        
        if not session_folder.exists():
            return {"jsonl": [], "csv": [], "metadata": []}
        
        files = {
            "jsonl": [],
            "csv": [], 
            "metadata": []
        }
        
        for file_path in session_folder.glob("*"):
            if file_path.suffix == '.jsonl':
                files["jsonl"].append(str(file_path))
            elif file_path.suffix == '.csv':
                files["csv"].append(str(file_path))
            elif 'metadata' in file_path.name:
                files["metadata"].append(str(file_path))
        
        return files
    
    def validate_stored_session(self, study_id: str, session_id: str) -> Dict[str, Any]:
        """Validate all stored data for a session."""
        files = self.get_session_files(study_id, session_id)
        
        results = {
            "study_id": study_id,
            "session_id": session_id,
            "validation_results": [],
            "total_errors": 0,
            "status": "valid"
        }
        
        for jsonl_path in files["jsonl"]:
            try:
                qa_turns = self.load_qa_turns(jsonl_path)
                errors = validate_qa_turns(qa_turns)
                
                file_result = {
                    "file": jsonl_path,
                    "turns_count": len(qa_turns),
                    "errors": errors,
                    "status": "valid" if not errors else "invalid"
                }
                
                results["validation_results"].append(file_result)
                results["total_errors"] += len(errors)
                
                if errors:
                    results["status"] = "invalid"
                    
            except Exception as e:
                results["validation_results"].append({
                    "file": jsonl_path,
                    "turns_count": 0,
                    "errors": [str(e)],
                    "status": "error"
                })
                results["total_errors"] += 1
                results["status"] = "error"
        
        return results


def create_sample_session() -> List[QATurn]:
    """Create sample Q/A turns for testing."""
    qa_turns = []
    
    personas = [
        {"id": "sarah_small_business", "name": "Sarah (Small Business)"},
        {"id": "mike_marketing_mgr", "name": "Mike (Marketing Manager)"},
        {"id": "jenny_freelancer", "name": "Jenny (Freelancer)"}
    ]
    
    questions = [
        "What are your biggest challenges with current social media management?",
        "How do you currently measure social media ROI?",
        "What features would you pay extra for in a social media tool?"
    ]
    
    answers = {
        "sarah_small_business": [
            "I'm constantly switching between tools - it's exhausting and inefficient.",
            "ROI is hard to track because data is scattered across platforms. I mostly look at follower growth.",
            "I'd pay for unified analytics and automated scheduling with smart timing suggestions."
        ],
        "mike_marketing_mgr": [
            "Getting approval workflows to work smoothly across our team is the biggest pain point.",
            "We need detailed attribution reporting to justify our social media budget to executives.", 
            "Advanced analytics, team collaboration features, and branded reporting would be worth premium pricing."
        ],
        "jenny_freelancer": [
            "Budget constraints mean I use free tools, but they're limited and unreliable.",
            "I track engagement rates manually - very time consuming but clients want to see results.",
            "I need affordable pricing with basic analytics. Can't afford enterprise features I won't use."
        ]
    }
    
    follow_ups = {
        "sarah_small_business": [
            "How much time do you spend daily switching between tools?",
            "What's your current monthly spend on social media tools?",
            "Would you pay $50/month for an all-in-one solution?"
        ],
        "mike_marketing_mgr": [
            "How many people are involved in your approval process?",
            "What attribution models do you currently use?",
            "What's your team's current tool budget?"
        ],
        "jenny_freelancer": [
            "What's your maximum monthly budget for social media tools?",
            "How many hours per month do you spend on manual tracking?",
            "Would you pay for a freelancer-specific tool package?"
        ]
    }
    
    follow_up_answers = {
        "sarah_small_business": [
            "About 30-45 minutes daily just switching and syncing data.",
            "Around $80/month across three different tools.",
            "Yes, if it truly replaced everything and saved me time."
        ],
        "mike_marketing_mgr": [
            "Usually 3-4 people: me, creative team lead, and final approval from director.",
            "We're trying to implement multi-touch attribution but it's complex.",
            "We have about $200/month budgeted for social media management tools."
        ],
        "jenny_freelancer": [
            "Ideally under $25/month - that's about what clients will reimburse.",
            "Probably 4-5 hours monthly just pulling numbers and creating reports.",
            "Absolutely - something designed for solo freelancers would be perfect."
        ]
    }
    
    # Generate Q/A turns
    turn_id = 1
    for round_id, question in enumerate(questions, 1):
        for persona in personas:
            persona_id = persona["id"]
            answer = answers[persona_id][round_id - 1]
            follow_up_q = follow_ups[persona_id][round_id - 1]
            follow_up_a = follow_up_answers[persona_id][round_id - 1]
            
            # Assign confidence based on persona and question
            confidence_map = {
                "sarah_small_business": [0.85, 0.70, 0.90],
                "mike_marketing_mgr": [0.80, 0.95, 0.85],  
                "jenny_freelancer": [0.75, 0.60, 0.80]
            }
            confidence = confidence_map[persona_id][round_id - 1]
            
            # Assign tags based on content
            tag_map = {
                1: ["workflow_inefficiency", "tool_fragmentation", "time_management"],
                2: ["analytics", "roi_measurement", "attribution"],
                3: ["pricing", "feature_prioritization", "willingness_to_pay"]
            }
            
            qa_turn = QATurn.create_with_timestamp(
                study_id="social_media_tool_study",
                session_id="session_001",
                persona_id=persona_id,
                round_id=round_id,
                question=question,
                answer=answer,
                confidence=confidence,
                tags=tag_map[round_id],
                follow_up_question=follow_up_q,
                follow_up_answer=follow_up_a
            )
            
            qa_turns.append(qa_turn)
    
    return qa_turns