"""
Input Handler Service
Receives and validates user input for the WriteCoach system
"""

import json
from typing import Dict, Optional

class InputHandler:
    def __init__(self):
        self.valid_formats = ['email', 'essay', 'report', 'creative', 'general']
    
    def validate_input(self, text: str, writing_format: Optional[str] = None) -> Dict:
        """
        Validate and prepare user input for processing
        
        Args:
            text: The text to analyze
            writing_format: Optional format specification
            
        Returns:
            Dict with validated input and metadata
        """
        if not text or not text.strip():
            return {
                'valid': False,
                'error': 'Text cannot be empty'
            }
        
        if len(text.strip()) < 10:
            return {
                'valid': False,
                'error': 'Text too short for meaningful analysis'
            }
        
        if writing_format and writing_format not in self.valid_formats:
            writing_format = 'general'
        
        return {
            'valid': True,
            'text': text.strip(),
            'format': writing_format or 'general',
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    def prepare_for_analysis(self, validated_input: Dict) -> Dict:
        """
        Prepare validated input for the analysis pipeline
        """
        if not validated_input.get('valid'):
            return validated_input
        
        return {
            'text': validated_input['text'],
            'metadata': {
                'format': validated_input['format'],
                'word_count': validated_input['word_count'],
                'char_count': validated_input['char_count']
            }
        }

# CLI interface for testing
if __name__ == "__main__":
    handler = InputHandler()
    
    print("WriteCoach Input Handler")
    print("-" * 30)
    
    text = input("Enter text to analyze: ")
    format_type = input("Enter format (email/essay/report/creative/general): ")
    
    result = handler.validate_input(text, format_type)
    
    if result['valid']:
        prepared = handler.prepare_for_analysis(result)
        print("\nInput validated successfully!")
        print(json.dumps(prepared, indent=2))
    else:
        print(f"\nError: {result['error']}")