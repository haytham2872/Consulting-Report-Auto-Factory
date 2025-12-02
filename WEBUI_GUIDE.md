# Web UI Quick Start Guide

## 🚀 Launch the Web Interface

### 1. Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

### 2. Set Your API Key

Make sure your `.env` file exists with your Anthropic API key:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Launch the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## ✨ Features

### Beautiful, Professional Interface
- Clean gradient header with branding
- Smooth fade-in animations
- Professional color scheme (purple gradients)
- Responsive layout

### Intuitive Workflow
1. **Upload CSVs**: Drag and drop your data files (orders, customers, etc.)
2. **Edit Brief**: Customize the business brief or use the default template
3. **Generate Report**: Click the button and watch the agents work
4. **View Results**: See your report in three different views

### Real-Time Progress Tracking
- Live status updates for each agent:
  - 🧠 Planning Agent: Creating analysis plan
  - 📊 Data Analyst Agent: Computing metrics
  - ✍️ Insights Agent: Writing report
- Progress bar showing 25% → 50% → 75% → 100%

### Three-Tab Results View

#### Tab 1: Report
- Professionally formatted markdown report
- Executive summary
- Key findings
- Data tables
- Recommendations

#### Tab 2: Analysis Data
- Visual metrics cards (Revenue, KPIs)
- Expandable sections for:
  - Analysis plan with objectives
  - Key performance indicators
  - Data tables
  - Raw JSON data

#### Tab 3: Download
- Download markdown report (`.md` file)
- Download analysis data (`.json` file)
- Files named with timestamps for easy tracking

## 🎨 Visual Design

### Color Palette
- Primary: Purple gradient (#667eea to #764ba2)
- Success: Green (#d4edda)
- Processing: Yellow (#fff3cd)
- Background: Light gray (#f8f9fa)
- Text: Dark gray (#666)

### Animations
- Smooth fade-in effects on all elements
- Spinner animation during processing
- Progress bar transitions

## 💡 Tips for Demo/Interview

1. **Pre-load sample data**: Have `orders.csv` and `customers.csv` ready
2. **Customize the brief**: Show how different briefs generate different insights
3. **Highlight the workflow**:
   - "Upload → Brief → Generate → View → Download"
4. **Emphasize automation**:
   - "This would take a consultant 4-8 hours, we do it in 2 minutes"
5. **Show the metadata**:
   - Model used, temperature, timestamps (reproducibility)
6. **Multi-file support**:
   - Upload multiple CSVs to show scalability

## 🔧 Customization Options

### Change Colors
Edit the CSS in `app.py` (lines 26-86):
```python
.main-header {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

### Modify Default Brief
Change lines 105-108 in `app.py` to customize the default business brief.

### Adjust Progress Messages
Modify status messages in lines 177-196 to customize agent descriptions.

## 📱 Responsive Design

The UI works on:
- Desktop (optimal)
- Tablet (good)
- Mobile (functional, but upload from desktop recommended)

## 🎯 For Deloitte Interview

### Key Talking Points:
1. **User Experience**: "No technical knowledge required - drag, drop, done"
2. **Speed**: "2 minutes vs. 4-8 hours for manual analysis"
3. **Consistency**: "Same high-quality output every time"
4. **Scalability**: "Process 50 clients overnight vs. 1 per analyst"
5. **Transparency**: "Full visibility into agent workflow and decisions"
6. **Professional Output**: "Client-ready reports with no post-processing"

### Demo Flow:
1. Open app (already running)
2. Upload sample data (have files ready)
3. Briefly explain the brief section
4. Click "Generate Report"
5. While processing, explain the 3-agent architecture
6. Show all three tabs when complete
7. Download files to show portability

### Questions You Might Get:
- **Q**: "What if we have different data structures?"
  - **A**: "The schema inference adapts to any CSV structure"

- **Q**: "Can we customize the analysis?"
  - **A**: "Yes - modify the brief to focus on specific metrics"

- **Q**: "How do we ensure accuracy?"
  - **A**: "Deterministic pandas calculations + LLM only for narrative"

- **Q**: "What about data security?"
  - **A**: "Runs locally, data never leaves your infrastructure"

- **Q**: "Can this integrate with our BI tools?"
  - **A**: "Yes - JSON output can feed into Tableau, PowerBI, etc."

## 🐛 Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### API Key Not Found
Make sure `.env` file has:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### Streamlit Caching Issues
```bash
streamlit cache clear
```

## 🎬 Video Demo Script

**[0:00-0:10]** "This is the Consulting Report Auto-Factory - an AI-powered business analysis tool"

**[0:10-0:20]** "Upload your CSV files - orders, customers, any business data"

**[0:20-0:30]** "Describe what insights you need in plain English"

**[0:30-0:40]** "Click Generate Report and watch our multi-agent system work"

**[0:40-0:50]** "Three AI agents collaborate: Planner, Analyst, and Insights"

**[0:50-1:00]** "In under 2 minutes, you get a full consulting report"

**[1:00-1:10]** "Executive summary, KPIs, tables, recommendations - all client-ready"

**[1:10-1:20]** "Download as Markdown or JSON for further processing"

**[1:20-1:30]** "What took 8 hours now takes 2 minutes. That's the power of agentic AI."
