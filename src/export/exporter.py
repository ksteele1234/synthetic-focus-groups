"""
Data exporter for JSON and CSV export functionality.
"""

import json
import csv
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.session import Session, SessionResponse


class DataExporter:
    """Handles export of focus group session data to various formats."""
    
    def __init__(self, export_path: str = "data/exports"):
        """Initialize data exporter with export path."""
        self.export_path = export_path
        os.makedirs(export_path, exist_ok=True)
    
    def export_session_json(self, session: Session, filepath: str = None) -> str:
        """Export session data to JSON format."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"session_{session.id}_{timestamp}.json")
        
        try:
            session_data = session.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            # Update session export records
            session.exported_formats.append('json')
            session.export_timestamps['json'] = datetime.now()
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting session to JSON: {e}")
    
    def export_session_csv(self, session: Session, filepath: str = None) -> str:
        """Export session data to CSV format (responses)."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"session_{session.id}_{timestamp}.csv")
        
        try:
            # Prepare CSV data from responses
            csv_data = []
            
            for response in session.responses:
                row = {
                    'session_id': response.session_id,
                    'response_id': response.id,
                    'sequence_number': response.sequence_number,
                    'timestamp': response.timestamp.isoformat(),
                    'response_type': response.response_type.value,
                    'speaker_id': response.speaker_id,
                    'speaker_name': response.speaker_name,
                    'speaker_type': response.speaker_type,
                    'content': response.content,
                    'question_id': response.question_id,
                    'responding_to_id': response.responding_to_id,
                    'duration_seconds': response.duration_seconds,
                    'sentiment_score': response.sentiment_score,
                    'emotion_tags': '; '.join(response.emotion_tags) if response.emotion_tags else '',
                    'key_themes': '; '.join(response.key_themes) if response.key_themes else ''
                }
                csv_data.append(row)
            
            # Write to CSV
            if csv_data:
                fieldnames = csv_data[0].keys()
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            # Update session export records
            session.exported_formats.append('csv')
            session.export_timestamps['csv'] = datetime.now()
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting session to CSV: {e}")
    
    def export_session_summary_csv(self, session: Session, filepath: str = None) -> str:
        """Export session summary data to CSV format."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"session_summary_{session.id}_{timestamp}.csv")
        
        try:
            # Create summary data
            summary_data = [
                {
                    'session_id': session.id,
                    'session_name': session.name,
                    'project_id': session.project_id,
                    'facilitator_id': session.facilitator_id,
                    'status': session.status,
                    'started_at': session.started_at.isoformat() if session.started_at else '',
                    'ended_at': session.ended_at.isoformat() if session.ended_at else '',
                    'duration_minutes': session.actual_duration_minutes,
                    'participant_count': len(session.participant_ids),
                    'response_count': len(session.responses),
                    'key_insights': '; '.join(session.key_insights) if session.key_insights else '',
                    'themes_discovered': '; '.join(session.themes_discovered) if session.themes_discovered else '',
                    'overall_sentiment': session.overall_sentiment
                }
            ]
            
            # Write to CSV
            fieldnames = summary_data[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(summary_data)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting session summary to CSV: {e}")
    
    def export_participant_analysis_csv(self, session: Session, filepath: str = None) -> str:
        """Export participant-level analysis to CSV format."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"participant_analysis_{session.id}_{timestamp}.csv")
        
        try:
            # Calculate participant statistics
            participant_data = []
            
            for participant_id in session.participant_ids:
                participant_responses = session.get_responses_by_participant(participant_id)
                
                if participant_responses:
                    # Calculate statistics for this participant
                    response_count = len(participant_responses)
                    avg_response_length = sum(len(r.content) for r in participant_responses) / response_count
                    
                    # Calculate sentiment if available
                    sentiment_scores = [r.sentiment_score for r in participant_responses if r.sentiment_score is not None]
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else None
                    
                    # Collect themes
                    all_themes = []
                    for response in participant_responses:
                        all_themes.extend(response.key_themes)
                    unique_themes = list(set(all_themes))
                    
                    participant_data.append({
                        'session_id': session.id,
                        'participant_id': participant_id,
                        'participant_name': participant_responses[0].speaker_name,
                        'response_count': response_count,
                        'avg_response_length': round(avg_response_length, 1),
                        'avg_sentiment_score': round(avg_sentiment, 3) if avg_sentiment else '',
                        'unique_themes': '; '.join(unique_themes) if unique_themes else '',
                        'participant_summary': session.participant_summaries.get(participant_id, '')
                    })
            
            # Write to CSV
            if participant_data:
                fieldnames = participant_data[0].keys()
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(participant_data)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting participant analysis to CSV: {e}")
    
    def export_session_complete(self, session: Session, formats: List[str] = None) -> Dict[str, str]:
        """Export session in multiple formats and return filepaths."""
        if formats is None:
            formats = ['json', 'csv']
        
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if 'json' in formats:
                json_path = os.path.join(self.export_path, f"session_{session.id}_{timestamp}.json")
                exported_files['json'] = self.export_session_json(session, json_path)
            
            if 'csv' in formats:
                csv_path = os.path.join(self.export_path, f"session_responses_{session.id}_{timestamp}.csv")
                exported_files['csv'] = self.export_session_csv(session, csv_path)
            
            if 'summary' in formats or 'csv' in formats:
                summary_path = os.path.join(self.export_path, f"session_summary_{session.id}_{timestamp}.csv")
                exported_files['summary'] = self.export_session_summary_csv(session, summary_path)
            
            if 'participant_analysis' in formats:
                analysis_path = os.path.join(self.export_path, f"participant_analysis_{session.id}_{timestamp}.csv")
                exported_files['participant_analysis'] = self.export_participant_analysis_csv(session, analysis_path)
            
            return exported_files
            
        except Exception as e:
            raise Exception(f"Error during complete session export: {e}")
    
    def create_data_package(self, session: Session, include_metadata: bool = True) -> str:
        """Create a comprehensive data package for a session."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = os.path.join(self.export_path, f"session_package_{session.id}_{timestamp}")
        os.makedirs(package_dir, exist_ok=True)
        
        try:
            # Export all formats to the package directory
            formats = ['json', 'csv', 'summary', 'participant_analysis']
            
            for format_type in formats:
                if format_type == 'json':
                    filepath = os.path.join(package_dir, f"session_data.json")
                    self.export_session_json(session, filepath)
                elif format_type == 'csv':
                    filepath = os.path.join(package_dir, f"responses.csv")
                    self.export_session_csv(session, filepath)
                elif format_type == 'summary':
                    filepath = os.path.join(package_dir, f"session_summary.csv")
                    self.export_session_summary_csv(session, filepath)
                elif format_type == 'participant_analysis':
                    filepath = os.path.join(package_dir, f"participant_analysis.csv")
                    self.export_participant_analysis_csv(session, filepath)
            
            # Create metadata file if requested
            if include_metadata:
                metadata = {
                    'export_info': {
                        'export_timestamp': datetime.now().isoformat(),
                        'session_id': session.id,
                        'session_name': session.name,
                        'project_id': session.project_id,
                        'files_included': [
                            'session_data.json',
                            'responses.csv',
                            'session_summary.csv',
                            'participant_analysis.csv'
                        ]
                    },
                    'session_statistics': session.calculate_statistics()
                }
                
                metadata_file = os.path.join(package_dir, "metadata.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Create README file
            readme_content = f"""# Focus Group Session Data Package

## Session Information
- Session ID: {session.id}
- Session Name: {session.name}
- Project ID: {session.project_id}
- Status: {session.status}
- Duration: {session.actual_duration_minutes} minutes
- Participants: {len(session.participant_ids)}
- Responses: {len(session.responses)}

## Files Included

### session_data.json
Complete session data in JSON format including all responses, metadata, and analysis results.

### responses.csv  
Individual responses data in CSV format with participant information, timestamps, and content.

### session_summary.csv
High-level session summary with key metrics and insights.

### participant_analysis.csv
Participant-level analysis with response counts, sentiment scores, and themes.

### metadata.json
Export metadata and session statistics.

## Usage Notes
- All timestamps are in ISO format
- Sentiment scores range from -1.0 (negative) to 1.0 (positive)
- Themes and tags are separated by semicolons
- Export created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            readme_file = os.path.join(package_dir, "README.txt")
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            return package_dir
            
        except Exception as e:
            raise Exception(f"Error creating data package: {e}")
    
    def export_multiple_sessions(self, sessions: List[Session], combined: bool = True) -> Dict[str, Any]:
        """Export multiple sessions, optionally combining into single files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if combined:
            # Combine all sessions into single files
            export_dir = os.path.join(self.export_path, f"combined_sessions_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)
            
            # Combined JSON
            combined_data = {
                'export_info': {
                    'export_timestamp': datetime.now().isoformat(),
                    'session_count': len(sessions),
                    'session_ids': [s.id for s in sessions]
                },
                'sessions': [s.to_dict() for s in sessions]
            }
            
            json_file = os.path.join(export_dir, "combined_sessions.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            # Combined responses CSV
            all_responses = []
            for session in sessions:
                for response in session.responses:
                    response_dict = response.to_dict()
                    response_dict['session_name'] = session.name
                    all_responses.append(response_dict)
            
            if all_responses:
                csv_file = os.path.join(export_dir, "combined_responses.csv")
                fieldnames = all_responses[0].keys()
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_responses)
            
            return {
                'type': 'combined',
                'export_dir': export_dir,
                'files': {
                    'json': json_file,
                    'csv': csv_file if all_responses else None
                }
            }
        
        else:
            # Export each session separately
            individual_exports = {}
            
            for session in sessions:
                session_exports = self.export_session_complete(session)
                individual_exports[session.id] = session_exports
            
            return {
                'type': 'individual',
                'session_exports': individual_exports
            }
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get statistics about exported files."""
        if not os.path.exists(self.export_path):
            return {'total_files': 0, 'total_size_mb': 0}
        
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.export_path):
            total_files += len(files)
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'export_path': self.export_path
        }