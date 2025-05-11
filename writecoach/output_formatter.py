"""
Output Formatter Service
Formats analysis results and suggestions for user presentation
"""

from typing import Dict, List
import json
from datetime import datetime

class OutputFormatter:
    def __init__(self):
        self.colors = {
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'blue': '\033[94m',
            'end': '\033[0m'
        }
    
    def format_analysis_results(self, analysis: Dict, suggestions: Dict, 
                              format_rules: Dict = None, user_progress: Dict = None) -> str:
        """Format complete analysis results for display"""
        output = []
        
        # Header
        output.append(self._format_header())
        
        # Overall Score
        output.append(self._format_overall_score(analysis, format_rules))
        
        # Readability Analysis
        output.append(self._format_readability(analysis['readability']))
        
        # Issues Found
        output.append(self._format_issues(analysis))
        
        # Format-specific feedback
        if format_rules:
            output.append(self._format_rules_feedback(format_rules))
        
        # Improvement Suggestions
        output.append(self._format_suggestions(suggestions))
        
        # Progress tracking
        if user_progress and user_progress.get('status') == 'tracked':
            output.append(self._format_progress(user_progress))
        
        return '\n'.join(output)
    
    def _format_header(self) -> str:
        """Format report header"""
        return f"""
{self.colors['blue']}==================================================
                  WriteCoach Analysis Report
                  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=================================================={self.colors['end']}
"""
    
    def _format_overall_score(self, analysis: Dict, format_rules: Dict = None) -> str:
        """Format overall score section"""
        readability = analysis['readability']['score']
        
        # Determine color based on score
        if readability >= 60:
            color = self.colors['green']
        elif readability >= 40:
            color = self.colors['yellow']
        else:
            color = self.colors['red']
        
        score_section = f"""
{self.colors['blue']}OVERALL ASSESSMENT{self.colors['end']}
------------------
Readability Score: {color}{readability:.1f}/100{self.colors['end']} ({analysis['readability']['level']})
"""
        
        if format_rules and 'compliance_score' in format_rules:
            compliance = format_rules['compliance_score']
            compliance_color = self.colors['green'] if compliance > 0.8 else self.colors['yellow']
            score_section += f"Format Compliance: {compliance_color}{compliance:.0%}{self.colors['end']} ({format_rules['format']})\n"
        
        return score_section
    
    def _format_readability(self, readability: Dict) -> str:
        """Format readability section"""
        level = readability['level']
        score = readability['score']
        
        interpretation = {
            'Very Easy': 'Suitable for elementary school students',
            'Easy': 'Suitable for middle school students',
            'Fairly Easy': 'Suitable for high school students',
            'Standard': 'Suitable for college students',
            'Fairly Difficult': 'Suitable for college graduates',
            'Difficult': 'Suitable for professional/academic audience',
            'Very Difficult': 'Very complex - consider simplifying'
        }
        
        return f"""
{self.colors['blue']}READABILITY ANALYSIS{self.colors['end']}
-------------------
Level: {level}
Interpretation: {interpretation.get(level, 'Standard reading level')}
"""
    
    def _format_issues(self, analysis: Dict) -> str:
        """Format issues section"""
        style_issues = analysis['style_issues']
        grammar_issues = analysis['grammar_issues']
        
        output = f"\n{self.colors['blue']}ISSUES FOUND{self.colors['end']}\n-------------\n"
        
        if not style_issues and not grammar_issues:
            output += f"{self.colors['green']}✓ No major issues found{self.colors['end']}\n"
        else:
            if grammar_issues:
                output += f"\n{self.colors['red']}Grammar Issues ({len(grammar_issues)}){self.colors['end']}\n"
                for issue in grammar_issues[:3]:  # Show only first 3
                    output += f"• {issue['text']}: {issue['suggestion']}\n"
                if len(grammar_issues) > 3:
                    output += f"  ...and {len(grammar_issues) - 3} more\n"
            
            if style_issues:
                output += f"\n{self.colors['yellow']}Style Issues ({len(style_issues)}){self.colors['end']}\n"
                for issue in style_issues[:3]:  # Show only first 3
                    output += f"• {issue['text']}: {issue['suggestion']}\n"
                if len(style_issues) > 3:
                    output += f"  ...and {len(style_issues) - 3} more\n"
        
        return output
    
    def _format_rules_feedback(self, format_rules: Dict) -> str:
        """Format format-specific feedback"""
        output = f"\n{self.colors['blue']}FORMAT-SPECIFIC FEEDBACK{self.colors['end']}\n------------------------\n"
        output += f"Detected Format: {format_rules['format'].title()}\n"
        
        if format_rules['recommendations']:
            output += f"\n{self.colors['yellow']}Recommendations:{self.colors['end']}\n"
            for rec in format_rules['recommendations']:
                output += f"• {rec['issue']}: {rec['suggestion']}\n"
        
        if format_rules['format_specific_tips']:
            output += f"\n{self.colors['blue']}Tips for {format_rules['format'].title()} Writing:{self.colors['end']}\n"
            for tip in format_rules['format_specific_tips'][:3]:
                output += f"• {tip}\n"
        
        return output
    
    def _format_suggestions(self, suggestions: Dict) -> str:
        """Format improvement suggestions"""
        output = f"\n{self.colors['blue']}IMPROVEMENT SUGGESTIONS{self.colors['end']}\n----------------------\n"
        
        if 'overall_feedback' in suggestions:
            output += f"{suggestions['overall_feedback']}\n"
        
        if 'specific_improvements' in suggestions and suggestions['specific_improvements']:
            output += f"\n{self.colors['yellow']}Specific Improvements:{self.colors['end']}\n"
            for imp in suggestions['specific_improvements'][:5]:
                priority_color = self.colors['red'] if imp['priority'] == 'high' else self.colors['yellow']
                output += f"• [{priority_color}{imp['priority']}{self.colors['end']}] {imp['suggestion']}\n"
        
        if 'rewrite_suggestions' in suggestions and suggestions['rewrite_suggestions']:
            output += f"\n{self.colors['blue']}Suggested Rewrites:{self.colors['end']}\n"
            for rewrite in suggestions['rewrite_suggestions'][:2]:
                output += f"Original: \"{rewrite['original'][:50]}...\"\n"
                output += f"Suggested: \"{rewrite['suggested'][:50]}...\"\n"
                output += f"Reason: {rewrite['reason']}\n\n"
        
        return output
    
    def _format_progress(self, progress: Dict) -> str:
        """Format progress tracking section"""
        output = f"\n{self.colors['blue']}YOUR PROGRESS{self.colors['end']}\n-------------\n"
        
        if progress.get('readability_change', 0) > 0:
            output += f"{self.colors['green']}✓ Readability improved by {progress['readability_change']:.1f} points{self.colors['end']}\n"
        
        if progress.get('grammar_improvement', 0) > 0:
            output += f"{self.colors['green']}✓ Grammar errors reduced by {progress['grammar_improvement']}{self.colors['end']}\n"
        
        output += f"Total submissions: {progress.get('total_submissions', 0)}\n"
        output += f"Days active: {progress.get('days_active', 0)}\n"
        output += f"Consistency score: {progress.get('consistency_score', 0):.0%}\n"
        
        return output
    
    def format_for_web(self, analysis: Dict, suggestions: Dict, 
                      format_rules: Dict = None, user_progress: Dict = None) -> Dict:
        """Format results for web display (JSON)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'readability_score': analysis['readability']['score'],
                'readability_level': analysis['readability']['level'],
                'format': format_rules.get('format', 'general') if format_rules else 'general',
                'compliance_score': format_rules.get('compliance_score') if format_rules else None,
                'total_issues': len(analysis['style_issues']) + len(analysis['grammar_issues'])
            },
            'analysis': analysis,
            'suggestions': suggestions,
            'format_rules': format_rules,
            'progress': user_progress,
            'quick_fixes': self._get_quick_fixes(analysis, suggestions)
        }
    
    def _get_quick_fixes(self, analysis: Dict, suggestions: Dict) -> List[Dict]:
        """Get quick fixes that can be applied immediately"""
        fixes = []
        
        # Grammar fixes
        for issue in analysis['grammar_issues'][:3]:
            fixes.append({
                'type': 'grammar',
                'description': issue['suggestion'],
                'priority': 'high'
            })
        
        # Style fixes
        for issue in analysis['style_issues'][:2]:
            fixes.append({
                'type': 'style',
                'description': issue['suggestion'],
                'priority': 'medium'
            })
        
        return fixes

# CLI interface for testing
if __name__ == "__main__":
    formatter = OutputFormatter()
    
    # Sample data for testing
    sample_analysis = {
        'readability': {'score': 55, 'level': 'Fairly Difficult'},
        'style_issues': [
            {'type': 'passive_voice', 'text': 'was written', 'suggestion': 'Use active voice'}
        ],
        'grammar_issues': [
            {'type': 'confused_words', 'text': 'their', 'suggestion': 'Check usage of their/there/they\'re'}
        ],
        'basic_stats': {'word_count': 150, 'sentence_count': 10},
        'sentence_analysis': {'variety_score': 0.4}
    }
    
    sample_suggestions = {
        'overall_feedback': 'Your writing shows good structure but could be clearer.',
        'specific_improvements': [
            {'type': 'clarity', 'suggestion': 'Break long sentences', 'priority': 'high'},
            {'type': 'style', 'suggestion': 'Use active voice', 'priority': 'medium'}
        ],
        'rewrite_suggestions': [
            {
                'original': 'The document was written by the team',
                'suggested': 'The team wrote the document',
                'reason': 'Active voice is clearer'
            }
        ]
    }
    
    sample_format_rules = {
        'format': 'email',
        'compliance_score': 0.85,
        'recommendations': [
            {'issue': 'Missing greeting', 'suggestion': 'Add a greeting like "Dear..."'}
        ],
        'format_specific_tips': ['Keep paragraphs short', 'Use clear subject line']
    }
    
    sample_progress = {
        'status': 'tracked',
        'readability_change': 5.2,
        'grammar_improvement': 2,
        'total_submissions': 5,
        'days_active': 3,
        'consistency_score': 0.8
    }
    
    # Test terminal formatting
    print("Terminal Output:")
    print(formatter.format_analysis_results(
        sample_analysis, 
        sample_suggestions, 
        sample_format_rules, 
        sample_progress
    ))
    
    # Test web formatting
    print("\n\nWeb Output (JSON):")
    web_output = formatter.format_for_web(
        sample_analysis, 
        sample_suggestions, 
        sample_format_rules, 
        sample_progress
    )
    print(json.dumps(web_output, indent=2))