"""
Suggestion Generator Service
Generates improvement suggestions using Gemini, OpenAI, or mock responses
"""

import os
from typing import Dict, List
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class SuggestionGenerator:
    def __init__(self, api_key: str = None):
        """
        Initialize with API key (tries Gemini first, then OpenAI)
        """
        # Try Google Gemini first (FREE!)
        self.gemini_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        self.client = None
        self.api_type = 'mock'
        
        # Initialize appropriate client
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')  # Updated model name
                self.api_type = 'gemini'
                print("Using Google Gemini API (FREE)")
            except ImportError:
                print("Google Generative AI package not installed. Falling back...")
            except Exception as e:
                print(f"Gemini initialization failed: {e}")
        
        if not self.client and self.openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.openai_key)
                self.api_type = 'openai'
                print("Using OpenAI API")
            except ImportError:
                print("OpenAI package not installed. Using mock responses...")
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
        
        if not self.client:
            print("Using mock responses")
    
    def generate_suggestions(self, text: str, analysis: Dict, writing_format: str) -> Dict:
        """
        Generate improvement suggestions based on analysis
        """
        print(f"Using {self.api_type} API")
        
        if self.api_type == 'gemini':
            return self._generate_gemini_suggestions(text, analysis, writing_format)
        elif self.api_type == 'openai':
            return self._generate_openai_suggestions(text, analysis, writing_format)
        else:
            return self._generate_mock_suggestions(text, analysis, writing_format)
    
    def _generate_gemini_suggestions(self, text: str, analysis: Dict, writing_format: str) -> Dict:
        """Generate suggestions using Gemini API"""
        try:
            prompt = self._create_prompt(text, analysis, writing_format)
            
            response = self.client.generate_content(prompt)
            response_text = response.text
            
            return self._parse_ai_response(response_text)
            
        except Exception as e:
            print(f"Gemini suggestion generation failed: {e}")
            return self._generate_mock_suggestions(text, analysis, writing_format)
    
    def _generate_openai_suggestions(self, text: str, analysis: Dict, writing_format: str) -> Dict:
        """Generate suggestions using OpenAI API"""
        try:
            prompt = self._create_prompt(text, analysis, writing_format)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional writing coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            return self._parse_ai_response(response_text)
            
        except Exception as e:
            print(f"OpenAI suggestion generation failed: {e}")
            return self._generate_mock_suggestions(text, analysis, writing_format)
    
    def _create_prompt(self, text: str, analysis: Dict, writing_format: str) -> str:
        """Create a prompt for the AI"""
        # Include detected issues in the prompt
        grammar_issues = analysis.get('grammar_issues', [])
        style_issues = analysis.get('style_issues', [])
        
        issues_text = ""
        if grammar_issues:
            issues_text += f"Grammar issues found: {[issue['text'] for issue in grammar_issues[:3]]}\n"
        if style_issues:
            issues_text += f"Style issues found: {[issue['text'] for issue in style_issues[:3]]}\n"
        
        return f"""
        Analyze this {writing_format} and provide specific improvement suggestions:
        
        Text: "{text}"
        
        Analysis results:
        - Readability: {analysis['readability']['level']}
        - Style issues: {len(style_issues)}
        - Grammar issues: {len(grammar_issues)}
        {issues_text}
        
        Please provide your response in JSON format with the following structure:
        {{
            "overall_feedback": "A brief overall assessment of the writing",
            "clarity_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
            "structure_suggestions": ["suggestion 1", "suggestion 2"],
            "grammar_corrections": [
                {{"error": "error text", "correction": "corrected text"}},
                {{"error": "error text", "correction": "corrected text"}}
            ],
            "improved_version": "A rewritten version of the text with all corrections applied"
        }}
        
        Make sure your response is valid JSON format.
        """
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                else:
                    json_str = response
            else:
                json_str = response
            
            parsed = json.loads(json_str)
            
            # Convert to the format expected by the rest of the system
            return {
                'overall_feedback': parsed.get('overall_feedback', 'No overall feedback provided'),
                'specific_improvements': self._convert_to_improvements(parsed),
                'rewrite_suggestions': self._create_rewrite_suggestions(parsed),
                'format_specific_tips': self._get_format_tips('general')
            }
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response[:200]}...")
            return self._generate_mock_suggestions("", {}, "general")
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._generate_mock_suggestions("", {}, "general")
    
    def _convert_to_improvements(self, parsed: Dict) -> List[Dict]:
        """Convert parsed AI response to improvement format"""
        improvements = []
        
        # Add clarity suggestions
        for idx, suggestion in enumerate(parsed.get('clarity_suggestions', [])):
            improvements.append({
                'type': 'clarity',
                'problem': f'Clarity issue {idx + 1}',
                'suggestion': suggestion,
                'priority': 'medium'
            })
        
        # Add structure suggestions
        for idx, suggestion in enumerate(parsed.get('structure_suggestions', [])):
            improvements.append({
                'type': 'structure',
                'problem': f'Structure issue {idx + 1}',
                'suggestion': suggestion,
                'priority': 'medium'
            })
        
        # Add grammar corrections
        for correction in parsed.get('grammar_corrections', []):
            if isinstance(correction, dict) and 'error' in correction and 'correction' in correction:
                improvements.append({
                    'type': 'grammar',
                    'problem': correction['error'],
                    'suggestion': f"Change to: {correction['correction']}",
                    'priority': 'high'
                })
        
        return improvements
    
    def _create_rewrite_suggestions(self, parsed: Dict) -> List[Dict]:
        """Create rewrite suggestions from parsed response"""
        improved_version = parsed.get('improved_version', '')
        if improved_version:
            return [{
                'original': 'Original text',
                'suggested': improved_version,
                'reason': 'AI suggested comprehensive improvement'
            }]
        return []
    
    def _generate_mock_suggestions(self, text: str, analysis: Dict, writing_format: str) -> Dict:
        """Generate mock suggestions for testing without API"""
        suggestions = {
            'overall_feedback': self._get_overall_feedback(analysis, writing_format),
            'specific_improvements': self._get_specific_improvements(analysis),
            'rewrite_suggestions': self._get_rewrite_suggestions(text, analysis),
            'format_specific_tips': self._get_format_tips(writing_format)
        }
        
        return suggestions
    
    def _get_overall_feedback(self, analysis: Dict, writing_format: str) -> str:
        """Generate overall feedback based on analysis"""
        readability = analysis.get('readability', {}).get('level', 'Unknown')
        
        if readability in ['Very Easy', 'Easy']:
            feedback = f"Your {writing_format} is very readable. Consider adding more sophisticated vocabulary where appropriate."
        elif readability in ['Standard', 'Fairly Easy']:
            feedback = f"Your {writing_format} has good readability. Minor improvements could enhance clarity."
        else:
            feedback = f"Your {writing_format} might be difficult to read. Consider simplifying complex sentences."
        
        return feedback
    
    def _get_specific_improvements(self, analysis: Dict) -> List[Dict]:
        """Get specific improvement suggestions"""
        improvements = []
        
        # Based on style issues
        for issue in analysis.get('style_issues', []):
            improvements.append({
                'type': issue['type'],
                'problem': issue['text'],
                'suggestion': issue['suggestion'],
                'priority': 'medium'
            })
        
        # Based on grammar issues
        for issue in analysis.get('grammar_issues', []):
            improvements.append({
                'type': issue['type'],
                'problem': issue['text'],
                'suggestion': issue['suggestion'],
                'priority': 'high'
            })
        
        # Based on sentence analysis
        sentence_analysis = analysis.get('sentence_analysis', {})
        if sentence_analysis.get('variety_score', 1) < 0.3:
            improvements.append({
                'type': 'sentence_variety',
                'problem': 'Limited sentence variety',
                'suggestion': 'Mix different sentence types and lengths',
                'priority': 'low'
            })
        
        return improvements
    
    def _get_rewrite_suggestions(self, text: str, analysis: Dict) -> List[Dict]:
        """Suggest rewrites for problematic sentences"""
        sentences = text.split('.')
        rewrites = []
        
        # Find longest sentences
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 25:  # Long sentence threshold
                rewrites.append({
                    'original': sentence.strip(),
                    'suggested': self._simplify_sentence(sentence),
                    'reason': 'Sentence too long'
                })
        
        return rewrites
    
    def _simplify_sentence(self, sentence: str) -> str:
        """Basic sentence simplification"""
        words = sentence.split()
        if len(words) > 25:
            midpoint = len(words) // 2
            return f"{' '.join(words[:midpoint])}. {' '.join(words[midpoint:])}"
        return sentence
    
    def _get_format_tips(self, writing_format: str) -> List[str]:
        """Get format-specific writing tips"""
        tips = {
            'email': [
                "Start with a clear subject line",
                "Keep paragraphs short (2-3 sentences)",
                "End with a clear call to action"
            ],
            'essay': [
                "Include a strong thesis statement",
                "Use topic sentences for each paragraph",
                "Provide evidence for your claims"
            ],
            'report': [
                "Use headings and subheadings",
                "Include an executive summary",
                "Use bullet points for key information"
            ],
            'creative': [
                "Show, don't tell",
                "Use vivid sensory details",
                "Develop unique voice and style"
            ],
            'general': [
                "Be clear and concise",
                "Use appropriate tone for audience",
                "Proofread carefully"
            ]
        }
        
        return tips.get(writing_format, tips['general'])

# CLI interface for testing
if __name__ == "__main__":
    generator = SuggestionGenerator()
    
    # Test with a simple example
    sample_text = "i dont like grammer and speling is hard"
    sample_analysis = {
        'readability': {'level': 'Easy', 'score': 80},
        'style_issues': [],
        'grammar_issues': [
            {'type': 'spelling', 'text': 'dont', 'suggestion': 'Use "don\'t"'},
            {'type': 'spelling', 'text': 'grammer', 'suggestion': 'Use "grammar"'},
            {'type': 'spelling', 'text': 'speling', 'suggestion': 'Use "spelling"'}
        ],
        'sentence_analysis': {'variety_score': 0.5}
    }
    
    suggestions = generator.generate_suggestions(sample_text, sample_analysis, 'general')
    
    print("Suggestion Results:")
    print("=" * 30)
    for key, value in suggestions.items():
        print(f"{key}: {value}")
        print("-" * 20)