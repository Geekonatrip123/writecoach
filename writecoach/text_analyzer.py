"""
Text Analyzer Service
Performs comprehensive text analysis including grammar, style, and readability
"""

import os
import re
from typing import Dict, List
import nltk
from collections import Counter

# Explicitly add the NLTK data path
nltk.data.path.append('/home/samstark/nltk_data')

# Verify NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    print("NLTK data found successfully!")
except LookupError as e:
    print(f"NLTK data error: {e}")

class TextAnalyzer:
    def __init__(self):
        self.common_errors = {
            r'\b(their|there|they\'re)\b': 'their/there/they\'re',
            r'\b(your|you\'re)\b': 'your/you\'re',
            r'\b(its|it\'s)\b': 'its/it\'s',
            r'\b(affect|effect)\b': 'affect/effect',
            r'\b(then|than)\b': 'then/than'
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Perform comprehensive text analysis
        """
        analysis = {
            'basic_stats': self._get_basic_stats(text),
            'readability': self._calculate_readability(text),
            'style_issues': self._check_style(text),
            'grammar_issues': self._check_grammar(text),
            'sentence_analysis': self._analyze_sentences(text)
        }
        
        return analysis
    
    def _get_basic_stats(self, text: str) -> Dict:
        """Get basic text statistics"""
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        
        return {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'char_count': len(text),
            'unique_words': len(set(word.lower() for word in words if word.isalpha()))
        }
    
    def _calculate_readability(self, text: str) -> Dict:
        """Calculate readability scores"""
        sentences = nltk.sent_tokenize(text)
        words = nltk.word_tokenize(text)
        
        # Simple Flesch Reading Ease approximation
        if not sentences or not words:
            return {'score': 0, 'level': 'Unknown'}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = 1.5  # Simplified estimation
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        if flesch_score >= 90:
            level = "Very Easy"
        elif flesch_score >= 80:
            level = "Easy"
        elif flesch_score >= 70:
            level = "Fairly Easy"
        elif flesch_score >= 60:
            level = "Standard"
        elif flesch_score >= 50:
            level = "Fairly Difficult"
        elif flesch_score >= 30:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            'score': round(flesch_score, 2),
            'level': level
        }
    
    def _check_style(self, text: str) -> List[Dict]:
        """Check for style issues"""
        issues = []
        
        # Check for passive voice (simplified)
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
        words = nltk.word_tokenize(text.lower())
        
        for i, word in enumerate(words):
            if word in passive_indicators and i + 1 < len(words):
                if words[i + 1].endswith('ed') or words[i + 1].endswith('en'):
                    issues.append({
                        'type': 'passive_voice',
                        'text': f"{word} {words[i + 1]}",
                        'suggestion': 'Consider using active voice'
                    })
        
        # Check for wordiness
        wordy_phrases = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'in the event that': 'if',
            'at this point in time': 'now',
            'in spite of the fact that': 'although'
        }
        
        for phrase, replacement in wordy_phrases.items():
            if phrase in text.lower():
                issues.append({
                    'type': 'wordiness',
                    'text': phrase,
                    'suggestion': f'Replace with "{replacement}"'
                })
        
        return issues
    
    def _check_grammar(self, text: str) -> List[Dict]:
        """Check for common grammar issues"""
        issues = []
        
        # Check for common confused words
        for pattern, issue_type in self.common_errors.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'confused_words',
                    'text': match.group(),
                    'position': match.start(),
                    'suggestion': f'Check usage of {issue_type}'
                })
        
        # Check for repeated words
        words = text.split()
        for i in range(len(words) - 1):
            if words[i].lower() == words[i + 1].lower() and words[i].lower() not in ['the', 'a', 'an']:
                issues.append({
                    'type': 'repeated_word',
                    'text': words[i],
                    'suggestion': 'Remove repeated word'
                })
        
        return issues
    
    def _analyze_sentences(self, text: str) -> Dict:
        """Analyze sentence structure"""
        sentences = nltk.sent_tokenize(text)
        
        analysis = {
            'total_sentences': len(sentences),
            'sentence_types': [],
            'sentence_lengths': []
        }
        
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            analysis['sentence_lengths'].append(len(words))
            
            # Simple sentence type detection
            if sentence.endswith('?'):
                sent_type = 'question'
            elif sentence.endswith('!'):
                sent_type = 'exclamation'
            else:
                sent_type = 'statement'
            
            analysis['sentence_types'].append(sent_type)
        
        # Add sentence variety score
        type_counts = Counter(analysis['sentence_types'])
        analysis['variety_score'] = len(type_counts) / len(sentences) if sentences else 0
        
        return analysis

# CLI interface for testing
if __name__ == "__main__":
    analyzer = TextAnalyzer()
    
    # Test with sample text
    sample_text = """
    This is a sample text that we will analyze. It contains various sentences to test our analyzer.
    The analyzer will check for grammar issues, style problems, and calculate readability scores.
    Sometimes, people use passive voice when they should use active voice. This is a common issue.
    In order to improve writing, we need to identify these problems.
    """
    
    result = analyzer.analyze(sample_text)
    print("Text Analysis Results:")
    print("=" * 30)
    print(f"Basic Stats: {result['basic_stats']}")
    print(f"Readability: {result['readability']}")
    print(f"Style Issues: {result['style_issues']}")
    print(f"Grammar Issues: {result['grammar_issues']}")
    print(f"Sentence Analysis: {result['sentence_analysis']}")