"""
Main Pipeline - WriteCoach System
Orchestrates all microservices in the writing analysis pipeline
"""

from input_handler import InputHandler
from text_analyzer import TextAnalyzer
from format_classifier import FormatClassifier
from suggestion_generator import SuggestionGenerator
from progress_tracker import ProgressTracker
from output_formatter import OutputFormatter

class WriteCoachPipeline:
    def __init__(self):
        self.input_handler = InputHandler()
        self.text_analyzer = TextAnalyzer()
        self.format_classifier = FormatClassifier()
        self.suggestion_generator = SuggestionGenerator()
        self.progress_tracker = ProgressTracker()
        self.output_formatter = OutputFormatter()
    
    def process_text(self, text: str, user_id: str = "default_user", 
                     specified_format: str = None) -> str:
        """
        Process text through the complete analysis pipeline
        
        Args:
            text: The text to analyze
            user_id: User identifier for tracking progress
            specified_format: Optional format specification
            
        Returns:
            Formatted analysis results
        """
        # Step 1: Validate input
        validated_input = self.input_handler.validate_input(text, specified_format)
        
        if not validated_input['valid']:
            return f"Error: {validated_input['error']}"
        
        # Step 2: Prepare for analysis
        prepared_input = self.input_handler.prepare_for_analysis(validated_input)
        
        # Step 3: Analyze text
        analysis_results = self.text_analyzer.analyze(prepared_input['text'])
        
        # Step 4: Classify format and apply rules
        format_type, confidence = self.format_classifier.classify(
            prepared_input['text'], 
            specified_format
        )
        
        format_rules = self.format_classifier.apply_format_rules(
            prepared_input['text'], 
            format_type, 
            analysis_results
        )
        
        # Step 5: Generate suggestions
        suggestions = self.suggestion_generator.generate_suggestions(
            prepared_input['text'], 
            analysis_results, 
            format_type
        )
        
        # Step 6: Track progress
        progress_result = self.progress_tracker.track_submission(
            user_id, 
            analysis_results, 
            suggestions
        )
        
        # Step 7: Format output
        formatted_output = self.output_formatter.format_analysis_results(
            analysis_results,
            suggestions,
            format_rules,
            progress_result.get('overall_progress')
        )
        
        return formatted_output
    
    def get_user_report(self, user_id: str) -> str:
        """Generate a user progress report"""
        report = self.progress_tracker.get_user_report(user_id)
        
        if report.get('status') == 'no_data':
            return "No data found for user"
        
        # Format the report for display
        formatted_report = []
        formatted_report.append("\n" + "="*50)
        formatted_report.append("User Progress Report")
        formatted_report.append("="*50)
        
        if report.get('progress'):
            progress = report['progress']
            formatted_report.append(f"\nUser ID: {report.get('user_id', 'Unknown')}")
            formatted_report.append(f"Member since: {report.get('member_since', 'Unknown')}")
            formatted_report.append(f"Total submissions: {report.get('total_submissions', 0)}")
            
            if progress.get('status') == 'tracked':
                formatted_report.append(f"\nProgress Metrics:")
                formatted_report.append(f"- Readability change: {progress.get('readability_change', 0):+.1f} points")
                formatted_report.append(f"- Grammar improvement: {progress.get('grammar_improvement', 0)}")
                formatted_report.append(f"- Days active: {progress.get('days_active', 0)}")
                formatted_report.append(f"- Consistency score: {progress.get('consistency_score', 0):.0%}")
        
        if report.get('improvement_areas'):
            formatted_report.append("\nAreas for Improvement:")
            for area in report['improvement_areas']:
                formatted_report.append(f"- {area['area']}: {area['suggestion']}")
        
        return '\n'.join(formatted_report)

def main():
    """CLI interface for the WriteCoach system"""
    pipeline = WriteCoachPipeline()
    
    print("\n" + "="*50)
    print("       Welcome to WriteCoach v1.0")
    print("="*50 + "\n")
    
    while True:
        print("\nOptions:")
        print("1. Analyze text")
        print("2. View progress report")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\nText Analysis")
            print("-" * 20)
            
            # Get user ID
            user_id = input("Enter your user ID (or press Enter for default): ").strip()
            if not user_id:
                user_id = "default_user"
            
            # Get text
            print("\nEnter your text (type 'END' on a new line when finished):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            
            text = '\n'.join(lines)
            
            if not text.strip():
                print("No text entered. Please try again.")
                continue
            
            # Get format
            format_options = ['email', 'essay', 'report', 'creative', 'general']
            print(f"\nText format options: {', '.join(format_options)}")
            specified_format = input("Specify format (or press Enter for auto-detect): ").strip()
            
            if specified_format and specified_format not in format_options:
                specified_format = None
            
            # Process text
            print("\nAnalyzing your text...")
            result = pipeline.process_text(text, user_id, specified_format)
            print(result)
            
        elif choice == '2':
            user_id = input("Enter your user ID: ").strip()
            if not user_id:
                user_id = "default_user"
            
            report = pipeline.get_user_report(user_id)
            print(report)
            
        elif choice == '3':
            print("\nThank you for using WriteCoach! Keep writing!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()