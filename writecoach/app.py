"""
Streamlit Frontend for WriteCoach
A clean, interactive interface for the writing analysis system
"""

import streamlit as st
import json
from datetime import datetime
from main import WriteCoachPipeline
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="WriteCoach - Personal Writing Assistant",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize pipeline
@st.cache_resource
def get_pipeline():
    return WriteCoachPipeline()

pipeline = get_pipeline()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .suggestion-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1e88e5;
    }
    .issue-card {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("WriteCoach")
    st.markdown("Your personal writing assistant")
    
    # User ID input
    user_id = st.text_input("User ID", value="guest", help="Enter your user ID to track progress")
    
    # Text format selection
    format_options = ['Auto-detect', 'Email', 'Essay', 'Report', 'Creative', 'General']
    selected_format = st.selectbox("Text Format", format_options)
    
    if selected_format == 'Auto-detect':
        specified_format = None
    else:
        specified_format = selected_format.lower()
    
    st.markdown("---")
    
    # Navigation
    page = st.radio("Navigate", ["Analyze Text", "Progress Dashboard", "About"])

# Main content area
if page == "Analyze Text":
    st.title("✍️ Text Analysis")
    
    # Text input area
    text_input = st.text_area(
        "Enter your text here",
        height=300,
        placeholder="Paste or type your text here for analysis..."
    )
    
    # Analyze button
    if st.button("Analyze Text", type="primary"):
        if text_input.strip():
            with st.spinner("Analyzing your text..."):
                # Process text through pipeline
                result = pipeline.process_text(text_input, user_id, specified_format)
                
                # Parse the formatted output for display
                # Since we're using the terminal formatter, let's create a web-friendly version
                analysis_results = pipeline.text_analyzer.analyze(text_input)
                format_type, _ = pipeline.format_classifier.classify(text_input, specified_format)
                format_rules = pipeline.format_classifier.apply_format_rules(text_input, format_type, analysis_results)
                suggestions = pipeline.suggestion_generator.generate_suggestions(text_input, analysis_results, format_type)
                progress_result = pipeline.progress_tracker.track_submission(user_id, analysis_results, suggestions)
                
                # Display results in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Readability Score",
                        f"{analysis_results['readability']['score']:.1f}/100",
                        help=analysis_results['readability']['level']
                    )
                
                with col2:
                    st.metric(
                        "Format Compliance",
                        f"{format_rules['compliance_score']:.0%}",
                        help=f"Detected format: {format_rules['format']}"
                    )
                
                with col3:
                    total_issues = len(analysis_results['style_issues']) + len(analysis_results['grammar_issues'])
                    st.metric(
                        "Issues Found",
                        total_issues,
                        help="Grammar and style issues"
                    )
                
                # Tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "💡 Suggestions", "📈 Progress", "📝 Full Report"])
                
                with tab1:
                    st.subheader("Text Analysis")
                    
                    # Basic stats
                    st.markdown("### Basic Statistics")
                    stats_df = pd.DataFrame([analysis_results['basic_stats']])
                    st.dataframe(stats_df)
                    
                    # Issues
                    if analysis_results['grammar_issues'] or analysis_results['style_issues']:
                        st.markdown("### Issues Found")
                        
                        if analysis_results['grammar_issues']:
                            st.markdown("#### Grammar Issues")
                            for issue in analysis_results['grammar_issues']:
                                st.markdown(f"""
                                <div class="issue-card">
                                    <strong>{issue['type']}</strong>: {issue['text']}<br>
                                    💡 {issue['suggestion']}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        if analysis_results['style_issues']:
                            st.markdown("#### Style Issues")
                            for issue in analysis_results['style_issues']:
                                st.markdown(f"""
                                <div class="issue-card">
                                    <strong>{issue['type']}</strong>: {issue['text']}<br>
                                    💡 {issue['suggestion']}
                                </div>
                                """, unsafe_allow_html=True)
                
                with tab2:
                    st.subheader("Improvement Suggestions")
                    
                    # Overall feedback
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <h4>Overall Feedback</h4>
                        {suggestions['overall_feedback']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Specific improvements
                    if suggestions.get('specific_improvements'):
                        st.markdown("### Specific Improvements")
                        for imp in suggestions['specific_improvements']:
                            priority_color = "🔴" if imp['priority'] == 'high' else "🟡" if imp['priority'] == 'medium' else "🟢"
                            st.markdown(f"""
                            <div class="suggestion-card">
                                {priority_color} <strong>{imp['type']}</strong><br>
                                {imp['suggestion']}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Format-specific tips
                    if format_rules.get('format_specific_tips'):
                        st.markdown("### Writing Tips")
                        for tip in format_rules['format_specific_tips']:
                            st.markdown(f"• {tip}")
                
                with tab3:
                    st.subheader("Your Progress")
                    
                    if progress_result.get('overall_progress', {}).get('status') == 'tracked':
                        progress = progress_result['overall_progress']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                "Readability Change",
                                f"{progress.get('readability_change', 0):+.1f}",
                                help="Change since first submission"
                            )
                            st.metric(
                                "Total Submissions",
                                progress.get('total_submissions', 0)
                            )
                        
                        with col2:
                            st.metric(
                                "Grammar Improvement",
                                f"{progress.get('grammar_improvement', 0):+d}",
                                help="Reduction in grammar issues"
                            )
                            st.metric(
                                "Consistency Score",
                                f"{progress.get('consistency_score', 0):.0%}"
                            )
                        
                        # Progress visualization
                        if st.button("View Detailed Progress"):
                            report = pipeline.progress_tracker.get_user_report(user_id)
                            if report.get('submissions'):
                                # Create progress chart
                                submissions = report['submissions']
                                dates = [datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d') for s in submissions]
                                scores = [s['metrics']['readability_score'] for s in submissions]
                                
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', name='Readability Score'))
                                fig.update_layout(title='Readability Progress Over Time', xaxis_title='Date', yaxis_title='Score')
                                st.plotly_chart(fig)
                    else:
                        st.info("Submit more texts to track your progress!")
                
                with tab4:
                    st.subheader("Full Analysis Report")
                    st.code(result, language='text')
                    
                    # Download button
                    st.download_button(
                        label="Download Report",
                        data=result,
                        file_name=f"writecoach_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please enter some text to analyze.")

elif page == "Progress Dashboard":
    st.title("📈 Progress Dashboard")
    
    report = pipeline.progress_tracker.get_user_report(user_id)
    
    if report.get('status') == 'no_data':
        st.info("No submissions found. Start analyzing texts to see your progress!")
    else:
        # Progress metrics
        if report.get('progress', {}).get('status') == 'tracked':
            progress = report['progress']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Submissions", progress.get('total_submissions', 0))
            
            with col2:
                st.metric("Days Active", progress.get('days_active', 0))
            
            with col3:
                st.metric("Readability Change", f"{progress.get('readability_change', 0):+.1f}")
            
            with col4:
                st.metric("Consistency Score", f"{progress.get('consistency_score', 0):.0%}")
            
            # Progress visualization
            if report.get('submissions'):
                st.subheader("Progress Over Time")
                
                submissions = report['submissions']
                df = pd.DataFrame([
                    {
                        'Date': datetime.fromisoformat(s['timestamp']).strftime('%Y-%m-%d %H:%M'),
                        'Readability Score': s['metrics']['readability_score'],
                        'Grammar Issues': s['metrics']['grammar_issues_count'],
                        'Style Issues': s['metrics']['style_issues_count']
                    }
                    for s in submissions
                ])
                
                # Readability chart
                fig1 = px.line(df, x='Date', y='Readability Score', title='Readability Score Trend')
                st.plotly_chart(fig1)
                
                # Issues chart
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=df['Date'], y=df['Grammar Issues'], name='Grammar Issues', line=dict(color='red')))
                fig2.add_trace(go.Scatter(x=df['Date'], y=df['Style Issues'], name='Style Issues', line=dict(color='orange')))
                fig2.update_layout(title='Issues Over Time', xaxis_title='Date', yaxis_title='Number of Issues')
                st.plotly_chart(fig2)
                
                # Recent submissions
                st.subheader("Recent Submissions")
                st.dataframe(df.tail(5))
        
        # Achievements
        if report.get('achievements'):
            st.subheader("🏆 Achievements")
            for achievement in report['achievements']:
                st.success(f"**{achievement['name']}**: {achievement['description']}")
        
        # Improvement areas
        if report.get('improvement_areas'):
            st.subheader("Areas for Improvement")
            for area in report['improvement_areas']:
                priority_icon = "🔴" if area['priority'] == 'high' else "🟡"
                st.markdown(f"""
                <div class="suggestion-card">
                    {priority_icon} <strong>{area['area'].replace('_', ' ').title()}</strong><br>
                    {area['suggestion']}
                </div>
                """, unsafe_allow_html=True)

else:  # About page
    st.title("ℹ️ About WriteCoach")
    
    st.markdown("""
    ## Welcome to WriteCoach!
    
    WriteCoach is your personal AI-powered writing assistant that helps you improve your writing skills across different formats.
    
    ### Features
    
    - **Text Analysis**: Comprehensive analysis of grammar, style, and readability
    - **Format Detection**: Automatic detection of writing format (email, essay, report, etc.)
    - **Improvement Suggestions**: Personalized suggestions based on your writing style
    - **Progress Tracking**: Monitor your writing improvement over time
    - **Multiple Formats**: Support for emails, essays, reports, and creative writing
    
    ### How to Use
    
    1. Enter your User ID to track your progress
    2. Paste or type your text in the analysis area
    3. Select the text format (or let us auto-detect)
    4. Click "Analyze Text" to get instant feedback
    5. Review suggestions and improve your writing
    6. Track your progress over time in the dashboard
    
    ### Microservices Architecture
    
    WriteCoach is built using a microservices architecture with the following components:
    
    - **Input Handler**: Validates and prepares text for analysis
    - **Text Analyzer**: Performs comprehensive text analysis
    - **Format Classifier**: Identifies writing format and applies rules
    - **Suggestion Generator**: Creates improvement suggestions
    - **Progress Tracker**: Monitors user progress over time
    - **Output Formatter**: Presents results in a user-friendly format
    
    ### Privacy
    
    Your texts are processed locally and stored only for progress tracking purposes. 
    We respect your privacy and do not share your data.
    
    ---
    
    **Version**: 1.0.0  
    **Built with**: Python, Streamlit, NLTK, GenAI  
    **License**: MIT  
    """)
    
    # Display system status
    st.subheader("System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Text Analyzer: Online")
    
    with col2:
        st.success("✅ Format Classifier: Online")
    
    with col3:
        st.success("✅ Suggestion Generator: Online")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>WriteCoach v1.0 | Made with ❤️ for better writing</p>
    </div>
    """,
    unsafe_allow_html=True
)