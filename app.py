"""
Consulting Report Auto-Factory - Web UI
A beautiful, intuitive interface for automated business analysis and report generation.
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

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }

    /* Upload section styling */
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #667eea;
        margin-bottom: 1.5rem;
    }

    /* Results section styling */
    .results-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 2rem;
    }

    /* Status badge styling */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .status-success {
        background: #d4edda;
        color: #155724;
    }

    .status-processing {
        background: #fff3cd;
        color: #856404;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Smooth animations */
    .stMarkdown, .stFileUploader, .stTextArea {
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
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
    <h1>📊 Consulting Report Auto-Factory</h1>
    <p>AI-powered business analysis and report generation in minutes, not hours</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📁 Upload Your Data")
    st.markdown("Upload your CSV files containing business data (orders, customers, transactions, etc.)")

    uploaded_files = st.file_uploader(
        "Drag and drop CSV files here",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files with your business data"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
        with st.expander("📋 View uploaded files"):
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size / 1024:.1f} KB)")

with col2:
    st.markdown("### 📝 Business Brief")
    st.markdown("Describe what insights you're looking for")

    business_brief = st.text_area(
        "Enter your business brief",
        value="""We are an e-commerce retailer operating in Europe and North America.
This dataset contains orders over the past 18 months and a customer table.
We want to understand revenue trends, top segments, churn patterns, and identify opportunities to increase customer lifetime value.""",
        height=200,
        help="Describe your business context and what you want to analyze"
    )

# Action button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    generate_button = st.button(
        "🚀 Generate Report",
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
                        ⚙️ Processing your data...
                    </div>
                    <p style="color: #666; margin-top: 1rem;">
                        Our AI agents are analyzing your data and generating insights
                    </p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Stage 1: Planning
                status_text.text("🧠 Planning Agent: Creating analysis plan...")
                progress_bar.progress(25)

                try:
                    # Run the pipeline
                    run_pipeline(
                        input_dir=str(input_dir),
                        brief_path=str(brief_path),
                        reports_dir=str(reports_dir)
                    )

                    # Stage 2: Analysis
                    status_text.text("📊 Data Analyst Agent: Computing metrics...")
                    progress_bar.progress(50)

                    # Stage 3: Insights
                    status_text.text("✍️ Insights Agent: Writing report...")
                    progress_bar.progress(75)

                    # Stage 4: Complete
                    status_text.text("✅ Report generated successfully!")
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

                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    st.exception(e)
                    st.session_state.report_generated = False

# Display results
if st.session_state.report_generated and st.session_state.report_content:
    st.markdown("---")
    st.markdown("""
    <div class="status-badge status-success">
        ✅ Report Generated Successfully
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Report", "📊 Analysis Data", "💾 Download"])

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
                    st.metric("Model", metadata.get('model', 'N/A'))
                with col2:
                    st.metric("Temperature", metadata.get('temperature', 'N/A'))
                with col3:
                    if 'run_timestamp' in metadata:
                        timestamp = datetime.fromisoformat(metadata['run_timestamp'])
                        st.metric("Generated", timestamp.strftime("%Y-%m-%d %H:%M"))

            # Display plan
            if 'plan' in st.session_state.analysis_data:
                with st.expander("📋 Analysis Plan", expanded=True):
                    plan = st.session_state.analysis_data['plan']
                    st.markdown(f"**Title:** {plan.get('title', 'N/A')}")
                    st.markdown("**Objectives:**")
                    for obj in plan.get('objectives', []):
                        st.markdown(f"• {obj}")

            # Display KPIs
            if 'kpis' in st.session_state.analysis_data:
                with st.expander("📈 Key Performance Indicators", expanded=True):
                    kpis = st.session_state.analysis_data['kpis']

                    # Create metrics in columns
                    if kpis:
                        num_cols = min(4, len(kpis))
                        cols = st.columns(num_cols)
                        for idx, (key, value) in enumerate(kpis.items()):
                            with cols[idx % num_cols]:
                                # Format the value
                                if isinstance(value, (int, float)):
                                    if 'revenue' in key.lower() or 'amount' in key.lower() or 'value' in key.lower():
                                        formatted_value = f"${value:,.2f}"
                                    else:
                                        formatted_value = f"{value:,.2f}"
                                else:
                                    formatted_value = str(value)

                                st.metric(
                                    label=key.replace('_', ' ').title(),
                                    value=formatted_value
                                )

            # Display tables
            if 'tables' in st.session_state.analysis_data:
                with st.expander("📊 Data Tables", expanded=False):
                    for table in st.session_state.analysis_data['tables']:
                        st.markdown(f"**{table.get('title', 'Table')}**")
                        st.json(table.get('data', {}))

            # Raw JSON
            with st.expander("🔍 Raw JSON Data", expanded=False):
                st.json(st.session_state.analysis_data)

    with tab3:
        st.markdown("### Download Your Reports")

        col1, col2 = st.columns(2)

        with col1:
            # Download markdown report
            st.download_button(
                label="📄 Download Markdown Report",
                data=st.session_state.report_content,
                file_name=f"consulting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            # Download JSON data
            if st.session_state.analysis_data:
                st.download_button(
                    label="📊 Download Analysis Data (JSON)",
                    data=json.dumps(st.session_state.analysis_data, indent=2),
                    file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>Powered by Claude AI • Built for automated business intelligence</p>
</div>
""", unsafe_allow_html=True)
