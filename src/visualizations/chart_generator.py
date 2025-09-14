"""
Chart generator that converts visualization specifications into actual PNG/SVG files.
Implements the charts requested: themes, pain points frequency, feature votes, sentiment analysis.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Set style preferences
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class ChartGenerator:
    """Generate actual chart files from visualization specifications."""
    
    def __init__(self, output_dir: str = "data/charts"):
        """Initialize chart generator."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Chart styling
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'accent': '#F18F01',
            'success': '#C73E1D',
            'neutral': '#6B7280'
        }
        
        self.color_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6B7280', '#10B981', '#8B5CF6']
    
    def generate_theme_frequency_chart(self, themes_data: List[Dict[str, Any]], 
                                     session_id: str = None,
                                     format: str = 'png') -> str:
        """Generate theme frequency bar chart."""
        if not themes_data:
            themes_data = self._get_mock_themes_data()
        
        # Prepare data
        df = pd.DataFrame(themes_data)
        df = df.sort_values('frequency', ascending=True)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(df['theme'], df['frequency'], color=self.color_palette[:len(df)])
        
        # Styling
        ax.set_xlabel('Frequency (Number of Mentions)', fontsize=12, fontweight='bold')
        ax.set_title('Top Themes by Frequency', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"theme_frequency_{session_id or 'demo'}_{timestamp}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_pain_points_chart(self, pain_points_data: List[Dict[str, Any]],
                                 session_id: str = None,
                                 format: str = 'png') -> str:
        """Generate pain points frequency chart (as specifically requested)."""
        if not pain_points_data:
            pain_points_data = self._get_mock_pain_points_data()
        
        # Create interactive plotly chart
        df = pd.DataFrame(pain_points_data)
        df = df.sort_values('mentions', ascending=False)
        
        fig = px.bar(df, x='pain_point', y='mentions',
                    title='😤 Pain Points Frequency',
                    labels={'pain_point': 'Pain Point', 'mentions': 'Number of Mentions'},
                    color='mentions',
                    color_continuous_scale='Reds')
        
        fig.update_layout(
            font=dict(size=12),
            title_font_size=16,
            height=500,
            showlegend=False
        )
        
        fig.update_xaxes(tickangle=45)
        
        # Save as HTML and PNG
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"pain_points_{session_id or 'demo'}_{timestamp}"
        
        # HTML version (interactive)
        html_filepath = os.path.join(self.output_dir, f"{base_filename}.html")
        fig.write_html(html_filepath)
        
        # PNG version (static)
        png_filepath = os.path.join(self.output_dir, f"{base_filename}.png")
        fig.write_image(png_filepath, width=1200, height=500)
        
        return png_filepath if format == 'png' else html_filepath
    
    def generate_sentiment_analysis_chart(self, sentiment_data: Dict[str, Any],
                                        session_id: str = None,
                                        format: str = 'png') -> str:
        """Generate sentiment analysis visualization."""
        if not sentiment_data:
            sentiment_data = self._get_mock_sentiment_data()
        
        # Create gauge chart for overall sentiment
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = sentiment_data.get('score', 0.5),
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Sentiment Score"},
            delta = {'reference': 0.5},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, 0.3], 'color': "#ffcccb"},
                    {'range': [0.3, 0.7], 'color': "#ffffcc"},
                    {'range': [0.7, 1], 'color': "#ccffcc"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9}}))
        
        fig.update_layout(
            height=400,
            title="Sentiment Analysis Dashboard",
            font={'size': 16}
        )
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"sentiment_analysis_{session_id or 'demo'}_{timestamp}"
        
        if format == 'html':
            filepath = os.path.join(self.output_dir, f"{base_filename}.html")
            fig.write_html(filepath)
        else:
            filepath = os.path.join(self.output_dir, f"{base_filename}.png")
            fig.write_image(filepath, width=800, height=400)
        
        return filepath
    
    def generate_feature_votes_chart(self, features_data: List[Dict[str, Any]],
                                   session_id: str = None,
                                   format: str = 'png') -> str:
        """Generate feature votes/requests chart."""
        if not features_data:
            features_data = self._get_mock_features_data()
        
        df = pd.DataFrame(features_data)
        df = df.sort_values('votes', ascending=True)
        
        # Create horizontal bar chart with matplotlib
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(df['feature'], df['votes'], color=self.color_palette[:len(df)])
        
        # Styling
        ax.set_xlabel('Number of Votes/Requests', fontsize=12, fontweight='bold')
        ax.set_title('Most Requested Features', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feature_votes_{session_id or 'demo'}_{timestamp}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_participant_engagement_chart(self, engagement_data: List[Dict[str, Any]],
                                           session_id: str = None,
                                           format: str = 'png') -> str:
        """Generate participant engagement levels chart."""
        if not engagement_data:
            engagement_data = self._get_mock_engagement_data()
        
        # Create bubble chart
        df = pd.DataFrame(engagement_data)
        
        fig = px.scatter(df, x='response_count', y='avg_sentiment', 
                        size='total_words', color='persona_weight',
                        hover_name='participant_name',
                        title='Participant Engagement Analysis',
                        labels={
                            'response_count': 'Number of Responses',
                            'avg_sentiment': 'Average Sentiment',
                            'total_words': 'Total Words',
                            'persona_weight': 'Persona Weight'
                        },
                        color_continuous_scale='Viridis')
        
        fig.update_layout(
            height=600,
            font=dict(size=12),
            title_font_size=16
        )
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"participant_engagement_{session_id or 'demo'}_{timestamp}"
        
        if format == 'html':
            filepath = os.path.join(self.output_dir, f"{base_filename}.html")
            fig.write_html(filepath)
        else:
            filepath = os.path.join(self.output_dir, f"{base_filename}.png")
            fig.write_image(filepath, width=1000, height=600)
        
        return filepath
    
    def generate_executive_dashboard(self, dashboard_data: Dict[str, Any],
                                  session_id: str = None,
                                  format: str = 'png') -> str:
        """Generate comprehensive executive dashboard."""
        # Create subplot dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Theme Distribution', 'Sentiment Overview', 
                          'Top Pain Points', 'Engagement Levels'],
            specs=[[{"type": "pie"}, {"type": "indicator"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Theme distribution (pie chart)
        themes = dashboard_data.get('themes', self._get_mock_themes_data())
        theme_names = [t['theme'][:20] for t in themes]
        theme_counts = [t['frequency'] for t in themes]
        
        fig.add_trace(go.Pie(labels=theme_names, values=theme_counts, name="Themes"),
                     row=1, col=1)
        
        # Sentiment gauge
        sentiment_score = dashboard_data.get('sentiment', {}).get('score', 0.65)
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=sentiment_score,
            title={'text': "Overall Sentiment"},
            gauge={'axis': {'range': [0, 1]},
                   'bar': {'color': self.colors['primary']},
                   'steps': [{'range': [0, 0.5], 'color': "lightgray"},
                            {'range': [0.5, 1], 'color': "lightgreen"}]},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=2)
        
        # Pain points bar chart
        pain_points = dashboard_data.get('pain_points', self._get_mock_pain_points_data())
        pain_names = [p['pain_point'][:15] for p in pain_points[:5]]
        pain_counts = [p['mentions'] for p in pain_points[:5]]
        
        fig.add_trace(go.Bar(x=pain_names, y=pain_counts, name="Pain Points"),
                     row=2, col=1)
        
        # Engagement scatter
        engagement = dashboard_data.get('engagement', self._get_mock_engagement_data())
        fig.add_trace(go.Scatter(
            x=[e['response_count'] for e in engagement],
            y=[e['avg_sentiment'] for e in engagement],
            mode='markers+text',
            text=[e['participant_name'][:8] for e in engagement],
            textposition="top center",
            marker=dict(size=[e['total_words']/10 for e in engagement],
                       color=[e['persona_weight'] for e in engagement],
                       colorscale='Viridis'),
            name="Engagement"
        ), row=2, col=2)
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Executive Research Dashboard",
            title_font_size=20,
            title_x=0.5
        )
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"executive_dashboard_{session_id or 'demo'}_{timestamp}"
        
        if format == 'html':
            filepath = os.path.join(self.output_dir, f"{base_filename}.html")
            fig.write_html(filepath)
        else:
            filepath = os.path.join(self.output_dir, f"{base_filename}.png")
            fig.write_image(filepath, width=1400, height=800)
        
        return filepath
    
    def generate_all_charts(self, session_data: Dict[str, Any], 
                          session_id: str = None,
                          formats: List[str] = ['png']) -> Dict[str, str]:
        """Generate all charts for a session."""
        charts_created = {}
        
        for format in formats:
            charts_created.update({
                f'theme_frequency_{format}': self.generate_theme_frequency_chart(
                    session_data.get('themes', []), session_id, format),
                f'pain_points_{format}': self.generate_pain_points_chart(
                    session_data.get('pain_points', []), session_id, format),
                f'sentiment_analysis_{format}': self.generate_sentiment_analysis_chart(
                    session_data.get('sentiment', {}), session_id, format),
                f'feature_votes_{format}': self.generate_feature_votes_chart(
                    session_data.get('features', []), session_id, format),
                f'participant_engagement_{format}': self.generate_participant_engagement_chart(
                    session_data.get('engagement', []), session_id, format),
                f'executive_dashboard_{format}': self.generate_executive_dashboard(
                    session_data, session_id, format)
            })
        
        return charts_created
    
    def _get_mock_themes_data(self) -> List[Dict[str, Any]]:
        """Generate mock themes data for demonstration."""
        return [
            {'theme': 'Pricing Concerns', 'frequency': 8, 'description': 'Cost and value concerns'},
            {'theme': 'Feature Requests', 'frequency': 6, 'description': 'Missing functionality'},
            {'theme': 'Usability Issues', 'frequency': 4, 'description': 'User experience problems'},
            {'theme': 'Integration Needs', 'frequency': 3, 'description': 'Third-party connections'},
            {'theme': 'Performance', 'frequency': 2, 'description': 'Speed and reliability'}
        ]
    
    def _get_mock_pain_points_data(self) -> List[Dict[str, Any]]:
        """Generate mock pain points data."""
        return [
            {'pain_point': 'Time Management', 'mentions': 15},
            {'pain_point': 'Cost Concerns', 'mentions': 12},
            {'pain_point': 'Complex Setup', 'mentions': 8},
            {'pain_point': 'Poor Support', 'mentions': 6},
            {'pain_point': 'Limited Features', 'mentions': 4}
        ]
    
    def _get_mock_sentiment_data(self) -> Dict[str, Any]:
        """Generate mock sentiment data."""
        return {
            'score': 0.65,
            'overall': 'positive',
            'confidence': 'high',
            'distribution': {
                'positive': 60,
                'neutral': 25,
                'negative': 15
            }
        }
    
    def _get_mock_features_data(self) -> List[Dict[str, Any]]:
        """Generate mock features data."""
        return [
            {'feature': 'API Integration', 'votes': 12},
            {'feature': 'Mobile App', 'votes': 10},
            {'feature': 'Advanced Analytics', 'votes': 8},
            {'feature': 'Team Collaboration', 'votes': 6},
            {'feature': 'Custom Workflows', 'votes': 4},
            {'feature': 'Better Notifications', 'votes': 3}
        ]
    
    def _get_mock_engagement_data(self) -> List[Dict[str, Any]]:
        """Generate mock engagement data."""
        return [
            {'participant_name': 'Sarah', 'response_count': 8, 'avg_sentiment': 0.7, 'total_words': 450, 'persona_weight': 3.0},
            {'participant_name': 'Mike', 'response_count': 6, 'avg_sentiment': 0.5, 'total_words': 320, 'persona_weight': 2.0},
            {'participant_name': 'Jenny', 'response_count': 4, 'avg_sentiment': 0.3, 'total_words': 180, 'persona_weight': 1.5},
            {'participant_name': 'Alex', 'response_count': 3, 'avg_sentiment': 0.6, 'total_words': 150, 'persona_weight': 1.0}
        ]


def create_charts_package(session_data: Dict[str, Any], 
                        session_id: str,
                        output_dir: str = None) -> str:
    """Create a complete charts package for a session."""
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"data/charts/session_{session_id}_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize chart generator with session-specific output
    generator = ChartGenerator(output_dir)
    
    # Generate all charts in both PNG and HTML formats
    charts = generator.generate_all_charts(session_data, session_id, ['png', 'html'])
    
    # Create manifest file
    manifest = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'charts_created': charts,
        'description': 'Complete visualization package for synthetic focus group session'
    }
    
    manifest_path = os.path.join(output_dir, 'manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return output_dir