# Multi-Agent Research System

An intelligent AI-powered research assistant with **dual research modes** that automatically selects the best sources and strategies for answering your questions using ArXiv papers and YouTube videos.

## 🌟 Features

- **🧠 Dual Research Modes**: 
  - **Deep Search**: Quick intelligent research across sources
  - **Deep Research**: Comprehensive multi-step analysis with question decomposition
- **📚 ArXiv Integration**: Searches academic papers with smart query generation
- **🎥 YouTube Integration**: Analyzes video transcripts for recent trends and tutorials  
- **🔗 Smart Synthesis**: Combines information from multiple sources with proper citations
- **🎯 Adaptive Strategy**: AI chooses between ArXiv, YouTube, or both based on your question
- **📊 Real-time Processing**: Live updates and intelligent loading messages
- **🔄 Toggle Interface**: Easy switching between research modes

## 🏗️ Architecture

### Research Modes

#### Deep Search Mode
- **PlannerAgent**: Fast strategy selection and execution
- **SynthesizerAgent**: Quick synthesis with citations

#### Deep Research Mode  
- **PlannerAgentDeepResearch**: Advanced multi-step research coordination
- **DecompositionAgent**: Breaks complex questions into sub-questions
- **SynthesizerAgentDeepResearch**: Comprehensive report generation with structured format

### Core Agents

1. **PlannerAgent / PlannerAgentDeepResearch**: Master coordinators that analyze queries and manage research strategy
2. **ArxivAgent**: Specialized for searching and processing academic papers
3. **YoutubeAgent**: Handles video search and transcript extraction
4. **SynthesizerAgent / SynthesizerAgentDeepResearch**: Combines and synthesizes information from all sources
5. **DecompositionAgent**: Breaks down complex questions (Deep Research only)

### Key Design Principles

- **Modular**: Each agent has a specific responsibility
- **Intelligent**: AI decides the best approach for each query
- **Extensible**: Easy to add new data sources
- **Robust**: Comprehensive error handling
- **Dual-Mode**: Flexible research depth based on user needs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini AI and YouTube)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd arxiv_agent
   ```

2. **Set up your Google API key:**
   ```bash
   export GOOGLE_API_KEY='your_api_key_here'
   ```

3. **Run the startup script:**
   ```bash
   ./start.sh
   ```

4. **Open your browser to:**
   ```
   http://localhost:8000
   ```

## 🔧 Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY='your_api_key_here'

# Test the system
python test_system.py

# Start the server
python main_multiagent.py
```

## 🎯 How It Works

### Research Mode Selection
Use the toggle in the interface to choose your research approach:

#### 🔍 Deep Search Mode (Default)
- **Fast & Efficient**: Quick intelligent research
- **Direct Analysis**: Analyzes your question and selects optimal sources
- **Streamlined**: Searches ArXiv and/or YouTube based on query type
- **Quick Synthesis**: Combines findings with citations

#### 🔬 Deep Research Mode  
- **Comprehensive**: Multi-step research process
- **Question Decomposition**: Breaks complex questions into sub-questions
- **Thorough Investigation**: Researches each component separately
- **Structured Reports**: Executive summary, findings, and conclusions
- **Enhanced Synthesis**: Holistic analysis across all sub-components

### 1. Query Analysis (Both Modes)
The system analyzes your question to determine:
- Whether academic papers are needed (ArXiv)
- Whether recent trends/tutorials are needed (YouTube)
- Complexity level and recency requirements

### 2. Research Execution

#### Deep Search Mode:
- Searches ArXiv for academic papers
- Searches YouTube for videos and extracts transcripts  
- Uses selected sources for comprehensive coverage

#### Deep Research Mode:
- **Step 1**: Decomposes question into 3-5 sub-questions
- **Step 2**: Researches each sub-question independently
- **Step 3**: Aggregates sources from all sub-question research
- **Step 4**: Creates comprehensive synthesis

### 3. Smart Synthesis (Both Modes)
The SynthesizerAgent:
- Combines information from all sources
- Adds proper citations [1], [2], etc.
- Creates coherent, well-structured reports
- **Deep Research**: Uses structured format with Executive Summary, Key Findings, and Conclusions

## 📝 Example Queries

The system excels at various types of research questions:

- **Academic**: "What are the latest developments in transformer models?"
- **Technical**: "How do diffusion models work for image generation?"  
- **Practical**: "Best practices for fine-tuning large language models"
- **Comparative**: "Differences between BERT and GPT architectures"
- **Complex** (Deep Research): "What are the implications of quantum computing for machine learning?"

## 🛠️ API Endpoints

- `GET /` - Web interface
- `GET /health` - System health check
- `POST /research` - Submit research query

### Research Parameters

- `question` (required): Your research question
- `research_mode` (optional): "deep_search" (default) or "deep_research"
- `max_sources` (optional): Maximum sources to retrieve (1-10, default: 5)
- `date_from` (optional): Filter ArXiv papers from this date
- `date_to` (optional): Filter ArXiv papers to this date

## 🔍 Advanced Configuration

### Environment Variables

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Customizing Agent Behavior

Each agent can be customized by modifying their respective files:

- `planner_agent.py` - Modify strategy selection logic
- `arxiv_agent.py` - Adjust search query generation
- `youtube_agent.py` - Change transcript processing
- `synthesizer_agent.py` - Customize report formatting

## 🧪 Testing

Run the system test to verify everything is working:

```bash
# Test both research modes
python test_both_modes.py

# Or test basic functionality
python test_system.py
```

## 🤝 Contributing

To extend the system:

1. Create new agents by inheriting from `BaseAgent`
2. Implement the required abstract methods
3. Add your agent to the `PlannerAgent` coordination logic
4. Update the strategy analysis in `analyze_query()`

## Acknowledgements
Thank you to **arXiv** for use of its open access interoperability.

This application uses the official **YouTube Data API** to fetch and display video information. By using this service, you are bound by the **YouTube Terms of Service**.
