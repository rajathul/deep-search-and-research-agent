# Multi‑Agent Research System

An AI-powered research assistant that orchestrates specialized agents to search, analyze, and synthesize findings from ArXiv papers, YouTube videos, and web pages. It features dual research modes, modern UX, and a clean, extensible architecture designed with engineering best practices recruiters love to see.

## Highlights

- Intelligent dual modes: Deep Search and Deep Research
- Modular agent architecture with clear separations of concern
- Pluggable model layer: Gemini via Google GenAI, or local OSS via Ollama
- ArXiv, YouTube, and Webpage analysis with citation-aware synthesis
- FastAPI backend, Jinja2 templates, and a polished, responsive frontend
- Production-friendly: health check, input validation, graceful error handling

## Architecture Overview

- Orchestration: `PlannerAgent`, `PlannerAgentDeepResearch`
- Retrieval: `ArxivAgent`, `YoutubeAgent`, `WebpageAgent`
- Reasoning & Synthesis: `SynthesizerAgent`, `SynthesizerAgentDeepResearch`
- Decomposition: `DecompositionAgent` (for Deep Research)

Data flow (simplified):
1) User submits question (+ optional URL/date range/source count) →
2) Planner selects strategy and sources →
3) Source agents fetch and process content →
4) Synthesizer produces a cited report →
5) Frontend renders with rich UI and typewriter effect.

Design principles:
- Modular components, easy to test and extend
- Clear agent contracts via `BaseAgent`
- Resilient error handling with informative logs
- Minimal coupling; simple to add new sources or models

## Tech Stack

- Backend: FastAPI, Python 3.8+
- LLM Clients: Google GenAI (`google-genai`), Ollama client
- Frontend: Jinja2, vanilla JS, Marked.js for Markdown rendering
- Integrations: ArXiv API, YouTube Data + transcripts, simple webpage crawler

## Quick Start

Prerequisites:
- Python 3.8+
- Google API key for Gemini (`GOOGLE_API_KEY`)
- For non-Gemini models: Ollama running locally at `http://localhost:11434` and an available model (e.g., `gemma3:4b`)

One‑command setup:
```bash
./start.sh
```
Then open: `http://localhost:8000`

Manual setup:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY='your_api_key_here'
python test_system.py
python main_multiagent.py
```

## Usage

- Enter your question and optionally a webpage URL to analyze alongside the research.
- Toggle between Deep Search (fast sweep) and Deep Research (decomposition + multi‑step synthesis).
- Choose the model: `gemma3:4b` (default), `gpt-oss:latest`, or `gemini-2.0-flash`.
- Use Advanced Options to set date filters and max sources.

Example cURL (form submission):
```bash
curl -X POST http://localhost:8000/research \
  -F 'question=How are diffusion models used for LLMs?' \
  -F 'research_mode=deep_search' \
  -F 'model=gemma3:4b' \
  -F 'max_sources=5' \
  -F 'date_from=2020-01-01' \
  -F 'date_to=2025-01-01' \
  -F 'webpage_url=https://example.com/blog/diffusion-and-llms'
```

## API

- `GET /` → Web UI
- `GET /health` → Health check
- `POST /research` → Research request

Parameters (form fields):
- `question` (required): research question
- `research_mode` (optional): `deep_search` or `deep_research`
- `model` (optional): `gemma3:4b`, `gpt-oss:latest`, or `gemini-2.0-flash`
- `max_sources` (optional): 1–10 (default 5)
- `date_from`, `date_to` (optional): range for ArXiv
- `webpage_url` (optional): analyze a specific page

## Development Notes

- Entry point: `main_multiagent.py`
- Frontend: `templates/index.html`, `static/script.js`, `static/style.css`
- Agents: `arxiv_agent.py`, `youtube_agent.py`, `webpage_agent.py`, `synthesizer_agent.py`, `planner_agent.py`, `planner_agent_deep_research.py`, `decomposition_agent.py`
- Base contracts: `base_agent.py` (handles model client selection and query generation)

Testing:
```bash
python test_both_modes.py
python test_system.py
```

## Deployment

Local server:
```bash
python main_multiagent.py   # runs uvicorn at http://localhost:8000
```

Vercel (serverless):
- `vercel.json` routes all paths to `main_multiagent.py` using `@vercel/python`.
- Ensure `GOOGLE_API_KEY` is set in Vercel project environment variables.

## Troubleshooting

- Webpage URL not reaching backend: hard refresh to clear cache. The app versions static assets with a query string to avoid this, but a forced reload ensures the latest `static/script.js` is used.
- Non‑Gemini models: make sure Ollama is installed, running, and the model name you pick exists locally (e.g., `ollama pull gemma:2b` or appropriate `gemma3:4b` variant). If you only use Gemini, the Google API key is sufficient.
- API key missing: the backend validates `GOOGLE_API_KEY` early. Set it before running.

## Roadmap

- Add more data sources (Semantic Scholar, arXiv categories, web search)
- Add vector cache for de‑duplication and faster synthesis context
- Richer planner reasoning traces and explainability panel in UI
- Dockerfile for standardized deployment

## Acknowledgements

Thanks to arXiv for open access interoperability. This application uses the YouTube Data API; usage is subject to YouTube’s Terms of Service.
