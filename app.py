"""
Consulting Report Auto-Factory - Web UI
Enterprise-grade interface for automated business analysis and report generation.
"""

import streamlit as st
import tempfile
import json
from pathlib import Path
from datetime import datetime
import shutil

from src.consulting_auto_factory.orchestrator import run_pipeline
from src.consulting_auto_factory.agents.qa_agent import QAAgent
from src.consulting_auto_factory.models import AnalysisResult

# Page configuration
st.set_page_config(
    page_title="Consulting Report Auto-Factory",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with updated color palette + gradient background
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Color Palette Variables */
    :root {
        --primary-accent: #2563EB;
        --hero-bg-left: #0F172A;
        --hero-bg-right: #1D4ED8;
        --page-bg-dark: #020617;
        --page-bg-mid: #0F172A;
        --page-bg-light: #1D4ED8;
        --card-bg: #FFFFFF;
        --surface-alt: #F9FAFB;
        --text-primary: #0F172A;
        --text-muted: #4B5563;
        --hero-text: #F9FAFB;
        --border-color: #E5E7EB;
        --success: #22C55E;
        --warning: #F97316;
        --error: #EF4444;
    }

    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding: 2rem 2rem 3rem 2rem;
        max-width: 1400px;
    }

    /* Animated gradient page background */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.25), transparent 55%),
            radial-gradient(circle at bottom right, rgba(8,47,73,0.85), transparent 60%),
            linear-gradient(135deg, var(--page-bg-dark), var(--page-bg-mid), var(--page-bg-light));
        background-size: 180% 180%;
        animation: gradientShift 28s ease-in-out infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Hero header with gradient (kept, but matches page) */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1D4ED8 100%);
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 24px rgba(15, 23, 42, 0.7);
    }

    .header-badge {
        display: inline-block;
        background: rgba(37, 99, 235, 0.25);
        color: #BFDBFE;
        padding: 0.35rem 0.9rem;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border: 1px solid rgba(96, 165, 250, 0.4);
    }

    .main-header h1 {
        color: #F9FAFB;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: #E5E7EB;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        font-weight: 400;
    }

    /* Section headers on dark gradient */
    h3, .stMarkdown h3 {
        color: #F9FAFB;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .section-desc {
        color: #CBD5F5;
        font-size: 0.875rem;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }

    /* File uploader - white card */
    [data-testid="stFileUploader"] {
        background: var(--card-bg) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
    }

    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-accent) !important;
        background: var(--surface-alt) !important;
    }

    [data-testid="stFileUploader"] section {
        border: none !important;
        padding: 0 !important;
    }

    [data-testid="stFileUploader"] small {
        color: var(--text-muted) !important;
    }

    [data-testid="stFileUploader"] label {
        color: var(--text-primary) !important;
    }

    /* Text area - white card */
    .stTextArea textarea {
        border: 2px solid var(--border-color) !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 1rem !important;
        background: var(--card-bg) !important;
        color: var(--text-primary) !important;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
    }

    .stTextArea textarea:focus {
        border-color: var(--primary-accent) !important;
        background: var(--card-bg) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
    }

    .stTextArea label {
        color: var(--text-primary) !important;
    }

    /* Primary buttons with accent color */
    .stButton > button {
        background: var(--primary-accent) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 999px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: #1D4ED8 !important;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.8) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:disabled {
        background: #4B5563 !important;
        color: #9CA3AF !important;
        box-shadow: none !important;
        opacity: 0.5 !important;
    }

    /* Success messages */
    .stSuccess {
        background: #F0FDF4 !important;
        color: #166534 !important;
        border: 1px solid #86EFAC !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 6px 18px rgba(22, 101, 52, 0.25);
    }

    /* Error messages */
    .stError {
        background: #FEF2F2 !important;
        color: #991B1B !important;
        border: 1px solid #FCA5A5 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        box-shadow: 0 6px 18px rgba(153, 27, 27, 0.25);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.25);
    }

    .streamlit-expanderHeader:hover {
        background: var(--surface-alt) !important;
        border-color: #D1D5DB !important;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.6rem 1.25rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.5rem 0;
    }

    .status-success {
        background: var(--success);
        color: #FFFFFF;
    }

    .status-processing {
        background: var(--warning);
        color: #FFFFFF;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(15, 23, 42, 0.6);
        padding: 0.4rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.6);
        backdrop-filter: blur(18px);
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.9rem;
        color: #E5E7EB;
        padding: 0.6rem 1.25rem;
        border-radius: 999px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(148, 163, 184, 0.25);
        color: #FFFFFF;
    }

    .stTabs [aria-selected="true"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetric"] {
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #22C55E, #2563EB);
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: rgba(15, 23, 42, 0.85) !important;
        color: #E5E7EB !important;
        border: 2px solid #2563EB !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.5rem !important;
        border-radius: 999px !important;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.6);
    }

    .stDownloadButton > button:hover {
        background: #2563EB !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.8);
    }

    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid rgba(148, 163, 184, 0.65);
    }

    /* Results container - white card for long text */
    .results-container {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.55);
        color: var(--text-primary);
    }

    .results-container .stMarkdown {
        color: var(--text-primary) !important;
    }

    /* Tables */
    .dataframe {
        border: 1px solid var(--border-color) !important;
        border-radius: 6px !important;
    }

    .dataframe th {
        background: var(--surface-alt) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
    }

    .dataframe td {
        color: var(--text-primary) !important;
    }

    /* Default markdown text on dark background */
    .stMarkdown {
        color: #E5E7EB;
    }

    /* Clean animations */
    .stMarkdown, .stFileUploader, .stTextArea {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Q&A Section */
    .qa-section {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.55);
        margin-top: 2rem;
    }

    .qa-header {
        color: var(--text-primary);
        font-size: 1.35rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .qa-subheader {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    .qa-pair {
        background: var(--surface-alt);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        animation: slideIn 0.3s ease-out;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .qa-question {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        padding-left: 1.5rem;
        position: relative;
    }

    .qa-question::before {
        content: "Q:";
        position: absolute;
        left: 0;
        color: var(--primary-accent);
        font-weight: 700;
    }

    .qa-answer {
        color: var(--text-primary);
        font-size: 0.9rem;
        line-height: 1.6;
        padding-left: 1.5rem;
        position: relative;
        border-left: 3px solid var(--primary-accent);
        padding-top: 0.25rem;
    }

    .qa-answer::before {
        content: "A:";
        position: absolute;
        left: -1.5rem;
        top: 0.25rem;
        color: var(--success);
        font-weight: 700;
    }

    .qa-input-container {
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'report_content' not in st.session_state:
    st.session_state.report_content = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

# Hero Header
st.markdown("""
<div class="main-header">
    <div class="header-badge">AI-Powered Intelligence</div>
    <h1>Consulting Report Auto-Factory</h1>
    <p>Transform business data into executive insights using multi-agent AI</p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Data Upload")
    st.markdown('<p class="section-desc">Upload CSV files containing your business data</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag and drop CSV files here",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload CSV files with your business data",
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) uploaded")
        with st.expander("View files"):
            for file in uploaded_files:
                st.markdown(f"• **{file.name}** · {file.size / 1024:.1f} KB")

with col2:
    st.markdown("### Business Brief")
    st.markdown('<p class="section-desc">Describe your analysis objectives and business context</p>', unsafe_allow_html=True)

    business_brief = st.text_area(
        "Enter your business brief",
        value="""We are an e-commerce retailer operating in Europe and North America.
This dataset contains orders over the past 18 months and a customer table.
We want to understand revenue trends, top segments, churn patterns, and identify opportunities to increase customer lifetime value.""",
        height=200,
        help="Describe your business and what insights you need",
        label_visibility="collapsed"
    )

# Action button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_button = st.button(
        "Generate Executive Report",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files or not business_brief
    )

# Process and display results
if generate_button:
    if uploaded_files and business_brief:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            reports_dir = temp_path / "reports"
            config_dir = temp_path / "config"

            input_dir.mkdir()
            config_dir.mkdir()
            reports_dir.mkdir()

            # Save files
            for uploaded_file in uploaded_files:
                file_path = input_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

            # Save brief
            brief_path = config_dir / "business_brief.txt"
            with open(brief_path, "w", encoding="utf-8") as f:
                f.write(business_brief)

            # Processing
            with st.spinner(""):
                st.markdown("""
                <div style="text-align: center; padding: 2rem;">
                    <div class="status-badge status-processing">Processing Analysis</div>
                    <p style="color: #E5E7EB; margin-top: 0.75rem;">AI agents are analyzing your data</p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.markdown('<p style="text-align: center; color: #E5E7EB;">Planning Agent: Creating strategy...</p>', unsafe_allow_html=True)
                    progress_bar.progress(25)

                    run_pipeline(
                        input_dir=str(input_dir),
                        brief_path=str(brief_path),
                        reports_dir=str(reports_dir)
                    )

                    status_text.markdown('<p style="text-align: center; color: #E5E7EB;">Data Analyst: Computing metrics...</p>', unsafe_allow_html=True)
                    progress_bar.progress(50)

                    status_text.markdown('<p style="text-align: center; color: #E5E7EB;">Insights Agent: Writing report...</p>', unsafe_allow_html=True)
                    progress_bar.progress(75)

                    status_text.markdown('<p style="text-align: center; color: #22C55E; font-weight: 600;">✓ Complete</p>', unsafe_allow_html=True)
                    progress_bar.progress(100)

                    # Load results
                    report_path = reports_dir / "consulting_report.md"
                    analysis_path = reports_dir / "analysis_summary.json"

                    if report_path.exists():
                        with open(report_path, "r", encoding="utf-8") as f:
                            st.session_state.report_content = f.read()

                    if analysis_path.exists():
                        with open(analysis_path, "r", encoding="utf-8") as f:
                            st.session_state.analysis_data = json.load(f)

                    st.session_state.report_generated = True
                    st.session_state.qa_history = []  # Clear Q&A history for new report
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.exception(e)
                    st.session_state.report_generated = False

# Display results
if st.session_state.report_generated and st.session_state.report_content:
    st.markdown("---")
    st.markdown('<div class="status-badge status-success">✓ Report Generated</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Executive Report", "Analytics Dashboard", "Export"])

    with tab1:
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.report_content)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        if st.session_state.analysis_data:
            st.markdown("### Analysis Overview")

            # Metadata
            if 'metadata' in st.session_state.analysis_data:
                metadata = st.session_state.analysis_data['metadata']
                col1, col2, col3 = st.columns(3)
                with col1:
                    model = metadata.get('model', 'N/A').replace('claude-3-', '').replace('-20240307', '').title()
                    st.metric("Model", model)
                with col2:
                    st.metric("Temperature", f"{metadata.get('temperature', 'N/A')}")
                with col3:
                    if 'run_timestamp' in metadata:
                        ts = datetime.fromisoformat(metadata['run_timestamp'])
                        st.metric("Generated", ts.strftime("%Y-%m-%d %H:%M"))

            st.markdown("")

            # Plan
            if 'plan' in st.session_state.analysis_data:
                with st.expander("Analysis Plan", expanded=True):
                    plan = st.session_state.analysis_data['plan']
                    st.markdown(f"**{plan.get('title', 'Plan')}**")
                    st.markdown("**Objectives:**")
                    for obj in plan.get('objectives', []):
                        st.markdown(f"• {obj}")

            # KPIs
            if 'kpis' in st.session_state.analysis_data:
                with st.expander("Key Performance Indicators", expanded=True):
                    kpis = st.session_state.analysis_data['kpis']

                    if kpis and isinstance(kpis, list):
                        cols = st.columns(min(3, len(kpis)))

                        for idx, kpi in enumerate(kpis):
                            with cols[idx % len(cols)]:
                                name = kpi.get('name', 'Unknown')
                                value = kpi.get('value', 0)
                                explanation = kpi.get('explanation', '')

                                # Format value
                                if isinstance(value, (int, float)):
                                    if any(w in name.lower() for w in ['revenue', 'amount', 'value', 'price', 'cost']):
                                        formatted = f"${value:,.2f}"
                                    elif any(w in name.lower() for w in ['rate', 'percent', '%']):
                                        formatted = f"{value:.1f}%"
                                    elif value > 1000:
                                        formatted = f"{value:,.0f}"
                                    else:
                                        formatted = f"{value:,.2f}"
                                else:
                                    formatted = str(value)

                                st.metric(label=name, value=formatted, help=explanation)

            # Tables
            if 'tables' in st.session_state.analysis_data:
                with st.expander("Data Tables", expanded=False):
                    for table in st.session_state.analysis_data['tables']:
                        st.markdown(f"**{table.get('title', 'Table')}**")
                        if table.get('description'):
                            st.caption(table['description'])

                        if 'columns' in table and 'rows' in table:
                            import pandas as pd
                            df = pd.DataFrame(table['rows'], columns=table['columns'])
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.json(table.get('data', {}))

            # Raw JSON
            with st.expander("Raw JSON", expanded=False):
                st.json(st.session_state.analysis_data)

    with tab3:
        st.markdown("### Export Reports")
        st.markdown('<p class="section-desc">Download your analysis in multiple formats</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("#### Executive Report")
            st.markdown("Client-ready narrative with insights")
            st.download_button(
                label="Download Markdown (.md)",
                data=st.session_state.report_content,
                file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            st.markdown("#### Analysis Data")
            st.markdown("Structured data with KPIs and metadata")
            if st.session_state.analysis_data:
                st.download_button(
                    label="Download JSON (.json)",
                    data=json.dumps(st.session_state.analysis_data, indent=2),
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

    # Q&A Section - Interactive follow-up questions
    st.markdown("---")
    st.markdown("""
    <div class="qa-section">
        <div class="qa-header">💬 Ask Follow-Up Questions</div>
        <div class="qa-subheader">Get instant answers about your analysis using AI</div>
    </div>
    """, unsafe_allow_html=True)

    # Q&A History Display (if any)
    if st.session_state.qa_history:
        st.markdown('<div class="qa-section" style="margin-top: 1rem; padding-top: 1rem;">', unsafe_allow_html=True)
        for qa in reversed(st.session_state.qa_history):  # Show most recent first
            st.markdown(f"""
            <div class="qa-pair">
                <div class="qa-question">{qa['question']}</div>
                <div class="qa-answer">{qa['answer']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Q&A Input
    with st.form("qa_form", clear_on_submit=True):
        question = st.text_input(
            "Your question:",
            placeholder="e.g., What are the main drivers of revenue growth? Which segment shows the most promise?",
            help="Ask questions about the analysis results, KPIs, or trends",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([3, 1, 3])
        with col2:
            ask_button = st.form_submit_button("Ask", use_container_width=True)

    # Handle Q&A submission
    if ask_button:
        if not question or not question.strip():
            st.warning("⚠️ Please enter a question first")
        else:
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    # Convert analysis_data dict to AnalysisResult object
                    analysis_result = AnalysisResult(**st.session_state.analysis_data)

                    # Get column roles if available
                    column_roles = st.session_state.analysis_data.get('column_roles', None)

                    # Initialize QA agent
                    qa_agent = QAAgent()

                    # Get answer
                    answer = qa_agent.answer_question(
                        question=question,
                        analysis_result=analysis_result,
                        column_roles=column_roles
                    )

                    # Add to history
                    st.session_state.qa_history.append({
                        'question': question,
                        'answer': answer,
                        'timestamp': datetime.now().isoformat()
                    })

                    # Rerun to show new Q&A
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
                    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #E5E7EB; padding: 2rem;">
    <p style="margin: 0; font-weight: 500; color: #F9FAFB;">Powered by Claude AI</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #CBD5F5;">Enterprise Business Intelligence · Secure & Confidential</p>
</div>
""", unsafe_allow_html=True)
