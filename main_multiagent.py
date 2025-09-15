# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from arxiv_agent import ArxivAgent
from youtube_agent import YoutubeAgent
from webpage_agent import WebpageAgent
from synthesizer_agent import SynthesizerAgent
import uvicorn
import traceback

app = FastAPI(title="Multi-Agent Research System", version="2.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Note: Agents will be created dynamically with the selected model

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
        "modes": ["all_sources"],
        "models": ["gemma3:4b", "gpt-oss:latest", "gemini-2.0-flash"],
        "default_model": "gemma3:4b",
        "agents": ["arxiv", "youtube", "webpage", "synthesizer"]
    }

@app.post("/research") 
async def research(
    request: Request,
    question: str = Form(...),
    research_mode: str = Form("all_sources"),
    model: str = Form("gemma3:4b"),
    webpage_url: str = Form("") ,
    date_from: str = Form(None),
    date_to: str = Form(None),
    max_sources: int = Form(5)
):
    """Research using all sources directly without planner agent."""
    if not question:
        return JSONResponse(content={'error': 'No question provided'}, status_code=400)
    
    # Note: webpage_url is optional; if empty we skip webpage analysis later
    if not webpage_url:
        print("INFO: No webpage URL provided - webpage analysis will be skipped if empty")
    else:
        print(f"INFO: Webpage URL provided in form: '{webpage_url}'")
    
    # Debug: Print all received form data
    # Extra visibility: show raw form fields received
    try:
        form_dump = await request.form()
        print(f"Raw form keys: {list(form_dump.keys())}")
        print(f"Raw form 'webpage_url': '{form_dump.get('webpage_url', '')}'")
    except Exception as _e:
        print(f"Could not dump raw form: {_e}")

    print(f"Form data received:")
    print(f"  question: '{question}'")
    print(f"  webpage_url: '{webpage_url}'")
    print(f"  model: '{model}'")
    print(f"  max_sources: {max_sources}")
    
    # Validate max_sources range
    if max_sources < 1:
        max_sources = 1
    elif max_sources > 10:
        max_sources = 10
    
    try:
        print(f"Researching with all sources using model: {model} for: {question}")
        
        # Create agents dynamically with the selected model
        arxiv_agent = ArxivAgent()
        youtube_agent = YoutubeAgent()
        webpage_agent = WebpageAgent()
        synthesizer_agent = SynthesizerAgent()
        
        # Update all agents to use the selected model
        arxiv_agent.update_model(model)
        youtube_agent.update_model(model)
        webpage_agent.update_model(model)
        webpage_agent.synthesizer_agent.update_model(model)
        synthesizer_agent.update_model(model)
        
        all_results = []
        all_sources = []
        
        # 1. Search ArXiv
        print("Searching ArXiv...")
        try:
            arxiv_results = arxiv_agent.run(
                user_question=question,
                max_sources=max_sources,
                date_from=date_from,
                date_to=date_to
            )
            if arxiv_results:
                all_results.append(f"**ArXiv Research:**\n{arxiv_results}")
                all_sources.extend(arxiv_results.get('sources', []))
                print("ArXiv search completed successfully")
        except Exception as e:
            print(f"ArXiv search failed: {e}")
            all_results.append(f"**ArXiv Research:** Failed to retrieve results - {str(e)}")
        
        # 2. Search YouTube
        print("Searching YouTube...")
        try:
            youtube_results = youtube_agent.run(
                user_question=question,
                max_sources=max_sources,
                transcript_limit=3000
            )
            if youtube_results:
                all_results.append(f"**YouTube Research:**\n{youtube_results}")
                all_sources.extend(youtube_results.get('sources', []))
                print("YouTube search completed successfully")
        except Exception as e:
            print(f"YouTube search failed: {e}")
            all_results.append(f"**YouTube Research:** Failed to retrieve results - {str(e)}")
        
        # 3. Search Webpage (if URL provided)
        print(f"Webpage URL received: '{webpage_url}'")  # Debug line
        if webpage_url and webpage_url.strip():
            print(f"Analyzing webpage: {webpage_url}")
            try:
                webpage_results = webpage_agent.run(
                    user_question=question,
                    url=webpage_url.strip()
                )
                if webpage_results:
                    all_results.append(f"**Webpage Analysis:**\n{webpage_results}")
                    all_sources.extend(webpage_results.get('sources', []))
                    print("Webpage analysis completed successfully")
                else:
                    print("Webpage analysis returned empty results")
            except Exception as e:
                print(f"Webpage analysis failed: {e}")
                print(f"Webpage error traceback: {traceback.format_exc()}")
                all_results.append(f"**Webpage Analysis:** Failed to analyze webpage - {str(e)}")
        else:
            print("No webpage URL provided or URL is empty")
        
        # 4. Synthesize all results
        if all_results:
            print("Synthesizing all results...")
            combined_research = "\n\n".join(all_results)
            
            # synthesis_prompt = f"""
            # Based on the following research from multiple sources, provide a comprehensive answer to the question: "{question}"

            # {combined_research}

            # Please synthesize this information into a coherent, well-structured response that:
            # 1. Directly addresses the user's question
            # 2. Integrates insights from all available sources
            # 3. Highlights any consensus or contradictions between sources
            # 4. Provides a balanced and informative conclusion
            # """
            
            try:
                # Use synthesizer's LLM directly instead of the run method that searches for sources
                final_answer = synthesizer_agent.synthesize(user_question=question, all_sources=all_sources)
                return JSONResponse(content={'answer': final_answer})
            except Exception as e:
                print(f"Synthesis failed: {e}")
                # If synthesis fails, return the raw results
                return JSONResponse(content={'answer': combined_research})
        else:
            return JSONResponse(content={'answer': 'No results found from any source. Please try a different question or check your parameters.'})
        
    except Exception as e:
        print(f"Research failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(content={'error': f'Research failed: {str(e)}'}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
