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

# Custom CSS for premium, sophisticated styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global styling with premium color palette */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Premium header with subtle pattern */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        padding: 3rem 3rem 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 3rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(circle at 20% 50%, rgba(6, 182, 212, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(5, 150, 105, 0.05) 0%, transparent 50%);
        pointer-events: none;
    }

    .main-header-content {
        position: relative;
        z-index: 1;
    }

    .header-badge {
        display: inline-block;
        background: rgba(5, 150, 105, 0.15);
        color: #10b981;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -1px;
        line-height: 1.2;
    }

    .main-header p {
        color: #94a3b8;
        margin: 0.75rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
        line-height: 1.6;
    }

    .header-accent {
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #06b6d4, #10b981);
        border-radius: 2px;
        margin-top: 1.5rem;
    }

    /* Section styling */
    .section-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .section-container:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .stMarkdown h3 {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .section-desc {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }

    /* Status badges with premium styling */
    .status-badge {
        display: inline-block;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
    }

    .status-processing {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
    }

    .status-info {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
    }

    /* Results container */
    .results-container {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        margin-top: 1.5rem;
        border: 1px solid #e2e8f0;
    }

    /* Premium metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        font-variant-numeric: tabular-nums;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    [data-testid="stMetric"] {
        background: #f8fafc;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        background: #ffffff;
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }

    /* Premium buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.875rem 2.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 14px rgba(8, 145, 178, 0.3);
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0e7490 0%, #155e75 100%);
        box-shadow: 0 6px 20px rgba(8, 145, 178, 0.4);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    .stButton > button:disabled {
        background: #e2e8f0;
        color: #94a3b8;
        box-shadow: none;
    }

    /* File uploader premium styling */
    [data-testid="stFileUploader"] {
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #0891b2;
        background: linear-gradient(135deg, #f0fdfa 0%, #f0f9ff 100%);
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.1);
    }

    /* Text area premium styling */
    .stTextArea textarea {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        padding: 1rem;
        transition: all 0.3s ease;
        background: #f8fafc;
    }

    .stTextArea textarea:focus {
        border-color: #0891b2;
        box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.1);
        background: #ffffff;
    }

    /* Premium tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        color: #64748b;
        padding: 0.75rem 1.75rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f1f5f9;
        color: #334155;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
        color: #0f172a;
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #06b6d4 0%, #10b981 100%);
        border-radius: 10px;
    }

    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }

    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Divider styling */
    hr {
        margin: 3rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }

    /* Smooth animations */
    .stMarkdown, .stFileUploader, .stTextArea, [data-testid="stMetric"] {
        animation: fadeInUp 0.5s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: #ffffff;
        color: #0f172a;
        border: 2px solid #0891b2;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }

    .stDownloadButton > button:hover {
        background: #0891b2;
        color: #ffffff;
        border-color: #0891b2;
        box-shadow: 0 4px 14px rgba(8, 145, 178, 0.3);
        transform: translateY(-2px);
    }

    /* Code/monospace elements */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: #f1f5f9;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #0f172a;
        font-size: 0.9em;
    }

    /* Tables */
    .dataframe {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    .dataframe th {
        background: #f8fafc !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.5px !important;
    }

    .dataframe td {
        color: #334155 !important;
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

# Premium Header
st.markdown("""
<div class="main-header">
    <div class="main-header-content">
        <div class="header-badge">AI-Powered Intelligence</div>
        <h1>Consulting Report Auto-Factory</h1>
        <p>Transform raw business data into actionable executive insights using multi-agent AI architecture</p>
        <div class="header-accent"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Data Upload")
    st.markdown('<p class="section-desc">Upload CSV files containing your business data for automated analysis</p>', unsafe_allow_html=True)

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
    st.markdown("### Business Context")
    st.markdown('<p class="section-desc">Describe your business objectives and the insights you need</p>', unsafe_allow_html=True)

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
        "Generate Executive Report",
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
                <div style="text-align: center; padding: 2.5rem;">
                    <div class="status-badge status-processing">
                        Processing Analysis
                    </div>
                    <p style="color: #64748b; margin-top: 1rem; font-size: 0.95rem;">
                        Multi-agent AI system is analyzing your data
                    </p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Stage 1: Planning
                status_text.markdown('<p style="text-align: center; color: #64748b; font-weight: 500;">Planning Agent: Designing analysis strategy...</p>', unsafe_allow_html=True)
                progress_bar.progress(25)

                try:
                    # Run the pipeline
                    run_pipeline(
                        input_dir=str(input_dir),
                        brief_path=str(brief_path),
                        reports_dir=str(reports_dir)
                    )

                    # Stage 2: Analysis
                    status_text.markdown('<p style="text-align: center; color: #64748b; font-weight: 500;">Data Analyst Agent: Computing business metrics...</p>', unsafe_allow_html=True)
                    progress_bar.progress(50)

                    # Stage 3: Insights
                    status_text.markdown('<p style="text-align: center; color: #64748b; font-weight: 500;">Insights Agent: Generating executive report...</p>', unsafe_allow_html=True)
                    progress_bar.progress(75)

                    # Stage 4: Complete
                    status_text.markdown('<p style="text-align: center; color: #10b981; font-weight: 600;">✓ Analysis Complete</p>', unsafe_allow_html=True)
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
    tab1, tab2, tab3 = st.tabs(["Executive Report", "Analytics Dashboard", "Export"])

    with tab1:
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.report_content)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        if st.session_state.analysis_data:
            st.markdown("### Analysis Overview")

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
                    st.markdown("**Strategic Objectives:**")
                    for obj in plan.get('objectives', []):
                        st.markdown(f"• {obj}")

            # Display KPIs
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
        st.markdown("### Export Reports")
        st.markdown('<p class="section-desc">Download your analysis results in multiple formats</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("#### Executive Report")
            st.markdown("Client-ready narrative with insights and strategic recommendations")
            st.download_button(
                label="Download Markdown (.md)",
                data=st.session_state.report_content,
                file_name=f"consulting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            st.markdown("#### Structured Data")
            st.markdown("Complete analysis data with KPIs, tables, and metadata")
            if st.session_state.analysis_data:
                st.download_button(
                    label="Download JSON (.json)",
                    data=json.dumps(st.session_state.analysis_data, indent=2),
                    file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Premium Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; padding: 2.5rem; font-size: 0.9rem;">
    <p style="margin: 0; font-weight: 500;">Powered by Claude AI</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem;">Enterprise-grade automated business intelligence · Secure & Confidential</p>
</div>
""", unsafe_allow_html=True)
