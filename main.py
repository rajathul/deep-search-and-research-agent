from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from agent import Agent
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/research")
async def research(question: str = Form(...)):
    if not question:
        return JSONResponse(content={'error': 'No question provided'}, status_code=400)

    agent = Agent()
    answer = agent.run(question)
    return JSONResponse(content={'answer': answer})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)