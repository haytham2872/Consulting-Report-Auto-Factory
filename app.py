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

# Page configuration
st.set_page_config(
    page_title="Consulting Report Auto-Factory",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for sophisticated, corporate styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main header styling - Corporate navy gradient */
    .main-header {
        background: linear-gradient(135deg, #1a2332 0%, #2c3e50 50%, #34495e 100%);
        padding: 2.5rem 3rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        border-left: 5px solid #0097A7;
    }

    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: #b8c5d6;
        margin: 0.75rem 0 0 0;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Section headers */
    .stMarkdown h3 {
        color: #2c3e50;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.3px;
    }

    /* Section descriptions */
    .section-desc {
        color: #5a6c7d;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    /* Status badge styling */
    .status-badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.95rem;
        margin: 0.5rem 0;
        letter-spacing: 0.3px;
    }

    .status-success {
        background: #e8f5e9;
        color: #2e7d32;
        border-left: 4px solid #43a047;
    }

    .status-processing {
        background: #fff3e0;
        color: #e65100;
        border-left: 4px solid #fb8c00;
    }

    .status-info {
        background: #e3f2fd;
        color: #1565c0;
        border-left: 4px solid #1976d2;
    }

    /* Results container */
    .results-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-top: 1.5rem;
        border: 1px solid #e8eef3;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 500;
        color: #5a6c7d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0097A7 0%, #00838F 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 151, 167, 0.3);
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #00838F 0%, #006064 100%);
        box-shadow: 0 6px 16px rgba(0, 151, 167, 0.4);
        transform: translateY(-1px);
    }

    .stButton > button:disabled {
        background: #cfd8dc;
        color: #90a4ae;
        box-shadow: none;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #f8fafb;
        border: 2px dashed #b0bec5;
        border-radius: 8px;
        padding: 1.5rem;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #0097A7;
        background: #f1f8f9;
    }

    /* Text area */
    .stTextArea textarea {
        border: 2px solid #e0e5e9;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        padding: 1rem;
    }

    .stTextArea textarea:focus {
        border-color: #0097A7;
        box-shadow: 0 0 0 3px rgba(0, 151, 167, 0.1);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #f8fafb;
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.95rem;
        color: #5a6c7d;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #0097A7;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 1rem;
        color: #2c3e50;
        background-color: #f8fafb;
        border-radius: 6px;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f1f5f7;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0097A7 0%, #00ACC1 100%);
    }

    /* Success message */
    .stSuccess {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 4px solid #43a047;
        border-radius: 6px;
        padding: 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e8eef3;
    }

    /* Smooth animations */
    .stMarkdown, .stFileUploader, .stTextArea {
        animation: fadeIn 0.4s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: #ffffff;
        color: #2c3e50;
        border: 2px solid #0097A7;
        font-weight: 500;
    }

    .stDownloadButton > button:hover {
        background: #0097A7;
        color: #ffffff;
        border-color: #0097A7;
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

# Header
st.markdown("""
<div class="main-header">
    <h1>Consulting Report Auto-Factory</h1>
    <p>Enterprise AI-powered business intelligence · Transform data into actionable insights in minutes</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Data Upload")
    st.markdown('<p class="section-desc">Upload your business data files in CSV format</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drag and drop CSV files here",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files containing your business data (orders, customers, transactions, etc.)",
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) uploaded successfully")
        with st.expander("View uploaded files"):
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
        help="Provide context about your business and specify what insights you're looking for",
        label_visibility="collapsed"
    )

# Action button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_button = st.button(
        "Generate Analysis Report",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files or not business_brief
    )

# Process and display results
if generate_button:
    if uploaded_files and business_brief:
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_dir = temp_path / "input"
            reports_dir = temp_path / "reports"
            config_dir = temp_path / "config"

            input_dir.mkdir()
            config_dir.mkdir()
            reports_dir.mkdir()

            # Save uploaded files
            for uploaded_file in uploaded_files:
                file_path = input_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

            # Save business brief
            brief_path = config_dir / "business_brief.txt"
            with open(brief_path, "w", encoding="utf-8") as f:
                f.write(business_brief)

            # Show processing animation
            with st.spinner(""):
                st.markdown("""
                <div style="text-align: center; padding: 2rem;">
                    <div class="status-badge status-processing">
                        Processing Analysis Request
                    </div>
                    <p style="color: #5a6c7d; margin-top: 1rem; font-size: 0.95rem;">
                        Multi-agent AI system analyzing your data and generating insights
                    </p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Stage 1: Planning
                status_text.markdown('<p style="text-align: center; color: #5a6c7d;">Planning Agent: Creating analysis strategy...</p>', unsafe_allow_html=True)
                progress_bar.progress(25)

                try:
                    # Run the pipeline
                    run_pipeline(
                        input_dir=str(input_dir),
                        brief_path=str(brief_path),
                        reports_dir=str(reports_dir)
                    )

                    # Stage 2: Analysis
                    status_text.markdown('<p style="text-align: center; color: #5a6c7d;">Data Analyst Agent: Computing business metrics...</p>', unsafe_allow_html=True)
                    progress_bar.progress(50)

                    # Stage 3: Insights
                    status_text.markdown('<p style="text-align: center; color: #5a6c7d;">Insights Agent: Generating executive report...</p>', unsafe_allow_html=True)
                    progress_bar.progress(75)

                    # Stage 4: Complete
                    status_text.markdown('<p style="text-align: center; color: #2e7d32; font-weight: 500;">✓ Analysis complete</p>', unsafe_allow_html=True)
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
                    st.rerun()

                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
                    st.exception(e)
                    st.session_state.report_generated = False

# Display results
if st.session_state.report_generated and st.session_state.report_content:
    st.markdown("---")
    st.markdown("""
    <div class="status-badge status-success">
        ✓ Report Generated Successfully
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Executive Report", "Analysis Data", "Download"])

    with tab1:
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.report_content)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        if st.session_state.analysis_data:
            st.markdown("### Analysis Summary")

            # Display metadata
            if 'metadata' in st.session_state.analysis_data:
                metadata = st.session_state.analysis_data['metadata']
                col1, col2, col3 = st.columns(3)
                with col1:
                    model_name = metadata.get('model', 'N/A').replace('claude-3-', '').replace('-20240307', '').title()
                    st.metric("AI Model", model_name)
                with col2:
                    st.metric("Temperature", f"{metadata.get('temperature', 'N/A')}")
                with col3:
                    if 'run_timestamp' in metadata:
                        timestamp = datetime.fromisoformat(metadata['run_timestamp'])
                        st.metric("Generated", timestamp.strftime("%Y-%m-%d %H:%M"))

            st.markdown("")  # Spacing

            # Display plan
            if 'plan' in st.session_state.analysis_data:
                with st.expander("Analysis Plan", expanded=True):
                    plan = st.session_state.analysis_data['plan']
                    st.markdown(f"**{plan.get('title', 'Analysis Plan')}**")
                    st.markdown("**Objectives:**")
                    for obj in plan.get('objectives', []):
                        st.markdown(f"• {obj}")

            # Display KPIs - FIXED: Iterate over list of KPI objects
            if 'kpis' in st.session_state.analysis_data:
                with st.expander("Key Performance Indicators", expanded=True):
                    kpis = st.session_state.analysis_data['kpis']

                    # Create metrics in columns
                    if kpis and isinstance(kpis, list):
                        num_cols = min(3, len(kpis))
                        cols = st.columns(num_cols)

                        for idx, kpi in enumerate(kpis):
                            with cols[idx % num_cols]:
                                # Extract KPI data
                                name = kpi.get('name', 'Unknown')
                                value = kpi.get('value', 0)
                                explanation = kpi.get('explanation', '')

                                # Format the value
                                if isinstance(value, (int, float)):
                                    if any(word in name.lower() for word in ['revenue', 'amount', 'value', 'price', 'cost']):
                                        formatted_value = f"${value:,.2f}"
                                    elif any(word in name.lower() for word in ['rate', 'percent', '%']):
                                        formatted_value = f"{value:.1f}%"
                                    elif value > 1000:
                                        formatted_value = f"{value:,.0f}"
                                    else:
                                        formatted_value = f"{value:,.2f}"
                                else:
                                    formatted_value = str(value)

                                st.metric(
                                    label=name,
                                    value=formatted_value,
                                    help=explanation
                                )

            # Display tables
            if 'tables' in st.session_state.analysis_data:
                with st.expander("Data Tables", expanded=False):
                    for table in st.session_state.analysis_data['tables']:
                        st.markdown(f"**{table.get('title', 'Table')}**")
                        if table.get('description'):
                            st.caption(table['description'])

                        # Try to format as proper table
                        if 'columns' in table and 'rows' in table:
                            import pandas as pd
                            df = pd.DataFrame(table['rows'], columns=table['columns'])
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.json(table.get('data', {}))

            # Raw JSON
            with st.expander("Raw JSON Data", expanded=False):
                st.json(st.session_state.analysis_data)

    with tab3:
        st.markdown("### Download Reports")
        st.markdown('<p class="section-desc">Export your analysis results for further processing or sharing</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("#### Markdown Report")
            st.markdown("Client-ready narrative report with executive summary, insights, and recommendations")
            st.download_button(
                label="Download Markdown (.md)",
                data=st.session_state.report_content,
                file_name=f"consulting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            st.markdown("#### Analysis Data")
            st.markdown("Structured JSON data with KPIs, tables, and complete analysis metadata")
            if st.session_state.analysis_data:
                st.download_button(
                    label="Download JSON (.json)",
                    data=json.dumps(st.session_state.analysis_data, indent=2),
                    file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #90a4ae; padding: 2rem; font-size: 0.9rem;">
    <p style="margin: 0;">Powered by Claude AI · Enterprise-grade automated business intelligence</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">Confidential & Secure · Data processed locally</p>
</div>
""", unsafe_allow_html=True)
