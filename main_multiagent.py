# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from planner_agent import PlannerAgent
from planner_agent_deep_research import PlannerAgentDeepResearch
import uvicorn
import traceback

app = FastAPI(title="Multi-Agent Research System", version="2.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize agents 
planner_agent = PlannerAgent()
planner_agent_deep_research = PlannerAgentDeepResearch()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "version": "2.0", 
        "modes": ["deep_search", "deep_research"],
        "agents": ["planner", "planner_deep_research", "arxiv", "youtube", "synthesizer", "decomposition"]
    }

@app.post("/research") 
async def research(
    question: str = Form(...),
    research_mode: str = Form("deep_search"),
    date_from: str = Form(None),
    date_to: str = Form(None),
    max_sources: int = Form(5)
):
    """Research using the intelligent planner agent that chooses the best strategy."""
    if not question:
        return JSONResponse(content={'error': 'No question provided'}, status_code=400)
    
    # Validate max_sources range
    if max_sources < 1:
        max_sources = 1
    elif max_sources > 10:
        max_sources = 10
    
    try:
        # Choose the appropriate planner based on research mode
        if research_mode == "deep_research":
            print(f"Using Deep Research mode for: {question}")
            answer = planner_agent_deep_research.run(
                user_question=question,
                max_sources=max_sources,
                date_from=date_from,
                date_to=date_to,
                transcript_limit=3000
            )
        else:
            print(f"Using Deep Search mode for: {question}")
            answer = planner_agent.run(
                user_question=question,
                max_sources=max_sources,
                date_from=date_from,
                date_to=date_to,
                transcript_limit=3000
            )
        
        return JSONResponse(content={'answer': answer})
    except Exception as e:
        print(f"Research failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(content={'error': f'Research failed: {str(e)}'}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)