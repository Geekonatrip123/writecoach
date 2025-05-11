"""
Progress Tracker Service
Tracks user writing improvement over time
"""

import json
import time
from datetime import datetime
from typing import Dict, List
import os

class ProgressTracker:
    def __init__(self, storage_path: str = "user_progress"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def track_submission(self, user_id: str, analysis_result: Dict, suggestions: Dict) -> Dict:
        """Track a new submission and update user progress"""
        submission = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis_result,
            'suggestions': suggestions,
            'metrics': self._extract_metrics(analysis_result)
        }
        
        # Load existing user data
        user_data = self._load_user_data(user_id)
        
        # Add new submission
        user_data['submissions'].append(submission)
        
        # Update overall progress
        user_data['progress'] = self._calculate_progress(user_data['submissions'])
        
        # Save updated data
        self._save_user_data(user_id, user_data)
        
        return {
            'submission_tracked': True,
            'current_metrics': submission['metrics'],
            'overall_progress': user_data['progress'],
            'improvement_areas': self._identify_improvement_areas(user_data['submissions'])
        }
    
    def _extract_metrics(self, analysis: Dict) -> Dict:
        """Extract key metrics from analysis"""
        return {
            'readability_score': analysis['readability']['score'],
            'readability_level': analysis['readability']['level'],
            'style_issues_count': len(analysis['style_issues']),
            'grammar_issues_count': len(analysis['grammar_issues']),
            'avg_sentence_length': analysis['basic_stats']['avg_words_per_sentence'],
            'sentence_variety': analysis['sentence_analysis']['variety_score'],
            'word_count': analysis['basic_stats']['word_count']
        }
    
    def _calculate_progress(self, submissions: List[Dict]) -> Dict:
        """Calculate overall progress from submission history"""
        if len(submissions) < 2:
            return {'status': 'insufficient_data', 'message': 'Need more submissions to track progress'}
        
        # Get first and last submissions
        first = submissions[0]['metrics']
        last = submissions[-1]['metrics']
        recent = submissions[-5:] if len(submissions) >= 5 else submissions
        
        # Calculate improvements
        readability_change = last['readability_score'] - first['readability_score']
        style_improvement = first['style_issues_count'] - last['style_issues_count']
        grammar_improvement = first['grammar_issues_count'] - last['grammar_issues_count']
        
        # Calculate trends
        recent_readability = [s['metrics']['readability_score'] for s in recent]
        readability_trend = 'improving' if recent_readability[-1] > recent_readability[0] else 'declining'
        
        return {
            'status': 'tracked',
            'total_submissions': len(submissions),
            'readability_change': round(readability_change, 2),
            'style_improvement': style_improvement,
            'grammar_improvement': grammar_improvement,
            'readability_trend': readability_trend,
            'days_active': self._calculate_days_active(submissions),
            'consistency_score': self._calculate_consistency_score(submissions)
        }
    
    def _identify_improvement_areas(self, submissions: List[Dict]) -> List[Dict]:
        """Identify areas that need improvement"""
        if not submissions:
            return []
        
        latest = submissions[-1]
        areas = []
        
        # Check readability
        if latest['metrics']['readability_score'] < 60:
            areas.append({
                'area': 'readability',
                'priority': 'high',
                'suggestion': 'Focus on simplifying complex sentences'
            })
        
        # Check grammar issues
        if latest['metrics']['grammar_issues_count'] > 3:
            areas.append({
                'area': 'grammar',
                'priority': 'high',
                'suggestion': 'Review common grammar rules'
            })
        
        # Check sentence variety
        if latest['metrics']['sentence_variety'] < 0.3:
            areas.append({
                'area': 'sentence_variety',
                'priority': 'medium',
                'suggestion': 'Mix different sentence types and lengths'
            })
        
        # Check style issues
        if latest['metrics']['style_issues_count'] > 5:
            areas.append({
                'area': 'writing_style',
                'priority': 'medium',
                'suggestion': 'Focus on active voice and concise language'
            })
        
        return areas
    
    def _calculate_days_active(self, submissions: List[Dict]) -> int:
        """Calculate number of days user has been active"""
        if not submissions:
            return 0
        
        dates = [datetime.fromisoformat(s['timestamp']).date() for s in submissions]
        return len(set(dates))
    
    def _calculate_consistency_score(self, submissions: List[Dict]) -> float:
        """Calculate consistency score based on submission frequency"""
        if len(submissions) < 2:
            return 0.0
        
        timestamps = [datetime.fromisoformat(s['timestamp']) for s in submissions]
        intervals = [(timestamps[i+1] - timestamps[i]).days for i in range(len(timestamps)-1)]
        
        if not intervals:
            return 0.0
        
        # Score is higher for regular submissions
        avg_interval = sum(intervals) / len(intervals)
        if avg_interval <= 1:
            return 1.0
        elif avg_interval <= 3:
            return 0.8
        elif avg_interval <= 7:
            return 0.6
        else:
            return 0.4
    
    def _load_user_data(self, user_id: str) -> Dict:
        """Load user data from storage"""
        file_path = os.path.join(self.storage_path, f"{user_id}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        
        # Create new user data
        return {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'submissions': [],
            'progress': {'status': 'new_user'}
        }
    
    def _save_user_data(self, user_id: str, data: Dict):
        """Save user data to storage"""
        file_path = os.path.join(self.storage_path, f"{user_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_report(self, user_id: str) -> Dict:
        """Generate a comprehensive progress report for user"""
        user_data = self._load_user_data(user_id)
        
        if not user_data['submissions']:
            return {'status': 'no_data', 'message': 'No submissions found'}
        
        return {
            'user_id': user_id,
            'member_since': user_data['created_at'],
            'total_submissions': len(user_data['submissions']),
            'progress': user_data['progress'],
            'recent_submissions': user_data['submissions'][-5:],
            'improvement_areas': self._identify_improvement_areas(user_data['submissions']),
            'achievements': self._calculate_achievements(user_data['submissions'])
        }
    
    def _calculate_achievements(self, submissions: List[Dict]) -> List[Dict]:
        """Calculate user achievements"""
        achievements = []
        
        if len(submissions) >= 5:
            achievements.append({
                'name': 'Getting Started',
                'description': 'Completed 5 writing submissions',
                'earned_at': submissions[4]['timestamp']
            })
        
        if len(submissions) >= 10:
            achievements.append({
                'name': 'Consistent Writer',
                'description': 'Completed 10 writing submissions',
                'earned_at': submissions[9]['timestamp']
            })
        
        # Check for improvement achievements
        if len(submissions) >= 3:
            recent_readability = [s['metrics']['readability_score'] for s in submissions[-3:]]
            if all(recent_readability[i] > recent_readability[i-1] for i in range(1, 3)):
                achievements.append({
                    'name': 'Rising Star',
                    'description': 'Improved readability for 3 consecutive submissions',
                    'earned_at': submissions[-1]['timestamp']
                })
        
        return achievements

# CLI interface for testing
if __name__ == "__main__":
    tracker = ProgressTracker()
    
    # Simulate multiple submissions for a user
    user_id = "test_user_123"
    
    # First submission
    analysis1 = {
        'readability': {'score': 45, 'level': 'Difficult'},
        'style_issues': [{'type': 'passive_voice'}, {'type': 'wordiness'}],
        'grammar_issues': [{'type': 'spelling'}],
        'basic_stats': {'avg_words_per_sentence': 25, 'word_count': 300},
        'sentence_analysis': {'variety_score': 0.2}
    }
    
    suggestions1 = {'overall_feedback': 'Needs improvement'}
    
    result1 = tracker.track_submission(user_id, analysis1, suggestions1)
    print("First submission tracked:")
    print(json.dumps(result1, indent=2))
    
    # Second submission (showing improvement)
    time.sleep(1)  # Simulate time passing
    analysis2 = {
        'readability': {'score': 55, 'level': 'Fairly Difficult'},
        'style_issues': [{'type': 'passive_voice'}],
        'grammar_issues': [],
        'basic_stats': {'avg_words_per_sentence': 20, 'word_count': 350},
        'sentence_analysis': {'variety_score': 0.4}
    }
    
    suggestions2 = {'overall_feedback': 'Showing improvement'}
    
    result2 = tracker.track_submission(user_id, analysis2, suggestions2)
    print("\nSecond submission tracked:")
    print(json.dumps(result2, indent=2))
    
    # Get user report
    report = tracker.get_user_report(user_id)
    print("\nUser Progress Report:")
    print(json.dumps(report, indent=2))