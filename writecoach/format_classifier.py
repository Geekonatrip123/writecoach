"""
Format Classifier Service
Identifies writing format and applies format-specific rules
"""

import re
from typing import Dict, Tuple

class FormatClassifier:
    def __init__(self):
        self.format_indicators = {
            'email': {
                'keywords': ['dear', 'sincerely', 'regards', 'best', 'hi', 'hello', 'subject:', 'from:', 'to:'],
                'patterns': [r'^(hi|hello|dear)\s+\w+', r'(sincerely|regards|best),?\s*$'],
                'structural': ['short_paragraphs', 'greeting', 'closing']
            },
            'essay': {
                'keywords': ['thesis', 'conclusion', 'furthermore', 'however', 'therefore', 'moreover', 'consequently'],
                'patterns': [r'first(ly)?[\s,]', r'second(ly)?[\s,]', r'finally[\s,]', r'in conclusion'],
                'structural': ['introduction', 'body_paragraphs', 'conclusion']
            },
            'report': {
                'keywords': ['executive summary', 'findings', 'recommendations', 'analysis', 'methodology', 'results'],
                'patterns': [r'\d+\.\d+', r'figure \d+', r'table \d+', r'section \d+'],
                'structural': ['headings', 'numbered_sections', 'data_presentation']
            },
            'creative': {
                'keywords': ['once upon', 'suddenly', 'meanwhile', 'whispered', 'shouted', 'felt', 'remembered'],
                'patterns': [r'"[^"]+?"', r'[.!?]\s*[A-Z][^.!?]*[.!?]'],
                'structural': ['dialogue', 'descriptive_language', 'narrative_flow']
            }
        }
        
        self.format_rules = {
            'email': {
                'max_length': 500,
                'preferred_paragraph_length': 50,
                'formality': 'semi-formal',
                'required_elements': ['greeting', 'body', 'closing']
            },
            'essay': {
                'min_length': 300,
                'preferred_paragraph_length': 150,
                'formality': 'formal',
                'required_elements': ['introduction', 'thesis', 'body', 'conclusion']
            },
            'report': {
                'min_length': 500,
                'preferred_paragraph_length': 100,
                'formality': 'formal',
                'required_elements': ['executive_summary', 'main_content', 'conclusions']
            },
            'creative': {
                'min_length': 200,
                'preferred_paragraph_length': 100,
                'formality': 'variable',
                'required_elements': ['narrative', 'characters_or_imagery']
            },
            'general': {
                'min_length': 50,
                'preferred_paragraph_length': 100,
                'formality': 'neutral',
                'required_elements': ['coherent_content']
            }
        }
    
    def classify(self, text: str, user_specified_format: str = None) -> Tuple[str, float]:
        """
        Classify the writing format
        Returns format type and confidence score
        """
        if user_specified_format and user_specified_format in self.format_rules:
            return user_specified_format, 1.0
        
        scores = {}
        
        for format_type, indicators in self.format_indicators.items():
            score = 0
            
            # Check keywords
            for keyword in indicators['keywords']:
                if keyword.lower() in text.lower():
                    score += 1
            
            # Check patterns
            for pattern in indicators['patterns']:
                if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                    score += 2
            
            # Check structural elements
            score += self._check_structure(text, indicators['structural'])
            
            scores[format_type] = score
        
        # Get format with highest score
        if scores:
            best_format = max(scores.items(), key=lambda x: x[1])
            total_score = sum(scores.values())
            confidence = best_format[1] / total_score if total_score > 0 else 0
            
            # If confidence is too low, default to general
            if confidence < 0.3:
                return 'general', confidence
            
            return best_format[0], confidence
        
        return 'general', 0.5
    
    def _check_structure(self, text: str, structural_elements: list) -> int:
        """Check for structural elements"""
        score = 0
        
        if 'short_paragraphs' in structural_elements:
            paragraphs = text.split('\n\n')
            avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
            if avg_length < 75:
                score += 1
        
        if 'greeting' in structural_elements:
            if re.match(r'^(dear|hi|hello)\s+\w+', text, re.IGNORECASE):
                score += 2
        
        if 'closing' in structural_elements:
            if re.search(r'(sincerely|regards|best|thanks),?\s*$', text, re.IGNORECASE | re.MULTILINE):
                score += 2
        
        if 'headings' in structural_elements:
            if re.search(r'^[A-Z][^.!?]*:?\s*$', text, re.MULTILINE):
                score += 2
        
        if 'dialogue' in structural_elements:
            if re.search(r'"[^"]+?"', text):
                score += 3
        
        return score
    
    def apply_format_rules(self, text: str, format_type: str, analysis: Dict) -> Dict:
        """Apply format-specific rules and generate recommendations"""
        rules = self.format_rules.get(format_type, self.format_rules['general'])
        recommendations = []
        compliance_score = 1.0
        
        # Check length requirements
        word_count = analysis['basic_stats']['word_count']
        
        if 'min_length' in rules and word_count < rules['min_length']:
            recommendations.append({
                'type': 'length',
                'issue': f"Text is too short for {format_type}",
                'suggestion': f"Expand to at least {rules['min_length']} words"
            })
            compliance_score *= 0.8
        
        if 'max_length' in rules and word_count > rules['max_length']:
            recommendations.append({
                'type': 'length',
                'issue': f"Text is too long for {format_type}",
                'suggestion': f"Reduce to maximum {rules['max_length']} words"
            })
            compliance_score *= 0.9
        
        # Check paragraph structure
        paragraphs = text.split('\n\n')
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        if avg_paragraph_length > rules['preferred_paragraph_length'] * 1.5:
            recommendations.append({
                'type': 'structure',
                'issue': 'Paragraphs are too long',
                'suggestion': f"Break into shorter paragraphs (~{rules['preferred_paragraph_length']} words)"
            })
            compliance_score *= 0.9
        
        # Check required elements
        missing_elements = self._check_required_elements(text, rules['required_elements'], format_type)
        
        for element in missing_elements:
            recommendations.append({
                'type': 'missing_element',
                'issue': f"Missing {element}",
                'suggestion': f"Add a clear {element} section"
            })
            compliance_score *= 0.85
        
        return {
            'format': format_type,
            'rules': rules,
            'recommendations': recommendations,
            'compliance_score': round(compliance_score, 2),
            'format_specific_tips': self._get_format_specific_tips(format_type)
        }
    
    def _check_required_elements(self, text: str, required_elements: list, format_type: str) -> list:
        """Check for missing required elements"""
        missing = []
        
        element_checks = {
            'greeting': lambda t: bool(re.search(r'^(dear|hi|hello)\s+\w+', t, re.IGNORECASE | re.MULTILINE)),
            'closing': lambda t: bool(re.search(r'(sincerely|regards|best|thanks),?\s*$', t, re.IGNORECASE | re.MULTILINE)),
            'introduction': lambda t: len(t.split('\n\n')[0].split()) > 30 if t.split('\n\n') else False,
            'thesis': lambda t: any(phrase in t.lower() for phrase in ['argue that', 'believe that', 'this essay will', 'this paper will']),
            'conclusion': lambda t: any(phrase in t.lower() for phrase in ['in conclusion', 'to conclude', 'therefore', 'in summary']),
            'executive_summary': lambda t: bool(re.search(r'(executive summary|summary|overview)', t, re.IGNORECASE)),
            'methodology': lambda t: bool(re.search(r'(methodology|methods|approach)', t, re.IGNORECASE)),
            'findings': lambda t: bool(re.search(r'(findings|results|outcomes)', t, re.IGNORECASE)),
            'recommendations': lambda t: bool(re.search(r'(recommend|suggest|propose)', t, re.IGNORECASE))
        }
        
        for element in required_elements:
            if element in element_checks:
                if not element_checks[element](text):
                    missing.append(element)
            elif element not in ['coherent_content', 'narrative', 'characters_or_imagery', 'body', 'main_content']:
                # These are more complex to check, so we skip them for now
                pass
        
        return missing
    
    def _get_format_specific_tips(self, format_type: str) -> list:
        """Get format-specific writing tips"""
        tips = {
            'email': [
                "Use a clear, descriptive subject line",
                "Start with a professional greeting",
                "Keep paragraphs concise (2-3 sentences)",
                "End with a specific call to action",
                "Include a professional signature"
            ],
            'essay': [
                "Start with a compelling hook",
                "Present a clear thesis statement",
                "Use topic sentences for each paragraph",
                "Provide evidence to support claims",
                "End with a strong conclusion that reinforces your thesis"
            ],
            'report': [
                "Begin with an executive summary",
                "Use clear section headings",
                "Present data visually when possible",
                "Keep language objective and factual",
                "Include actionable recommendations"
            ],
            'creative': [
                "Engage readers from the first line",
                "Show, don't tell - use sensory details",
                "Develop distinct character voices",
                "Maintain consistent point of view",
                "Create tension and resolution"
            ],
            'general': [
                "Know your audience",
                "Use clear, concise language",
                "Organize ideas logically",
                "Proofread for errors",
                "Maintain consistent tone"
            ]
        }
        
        return tips.get(format_type, tips['general'])

# CLI interface for testing
if __name__ == "__main__":
    classifier = FormatClassifier()
    
    # Test with different text samples
    email_sample = """
    Dear John,
    
    I hope this email finds you well. I wanted to follow up on our meeting yesterday.
    
    The project timeline looks good, and I think we can proceed as discussed.
    
    Best regards,
    Sarah
    """
    
    essay_sample = """
    The Impact of Technology on Modern Education
    
    In recent years, technology has fundamentally transformed the educational landscape. 
    This essay will examine how digital tools have revolutionized teaching methods, 
    enhanced student engagement, and created new challenges for educators.
    
    Firstly, digital platforms have made education more accessible than ever before.
    Students can now access course materials from anywhere in the world.
    
    Secondly, interactive learning tools have increased student engagement significantly.
    Virtual reality, gamification, and multimedia content make learning more engaging.
    
    In conclusion, while technology presents challenges, its benefits to education are undeniable.
    """
    
    print("Testing Format Classifier:")
    print("=" * 30)
    
    # Test email classification
    format_type, confidence = classifier.classify(email_sample)
    print(f"Email sample: {format_type} (confidence: {confidence:.2f})")
    
    # Test essay classification
    format_type, confidence = classifier.classify(essay_sample)
    print(f"Essay sample: {format_type} (confidence: {confidence:.2f})")
    
    # Test format rules application
    sample_analysis = {
        'basic_stats': {'word_count': 150}
    }
    
    rules_result = classifier.apply_format_rules(essay_sample, 'essay', sample_analysis)
    print(f"\nFormat rules for essay:")
    print(f"Compliance score: {rules_result['compliance_score']}")
    print(f"Recommendations: {rules_result['recommendations']}")
    print(f"Tips: {rules_result['format_specific_tips']}")