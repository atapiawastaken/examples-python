from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.client import client
import time
import uvicorn


# Define request model
class QueryRequest(BaseModel):
    file_data: list[tuple[str, str]]

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return "Welcome to the Defense Hackathon Groq Example"

@app.post("/api/transcribe")
async def schedule_workflow(request: QueryRequest):
    try:
        workflow_id = f"{int(time.time() * 1000)}-parent_workflow"
        
        runId = await client.schedule_workflow(
            workflow_name="ParentWorkflow",
            workflow_id=workflow_id,
            input={"file_data": request.file_data}
        )
        print("Scheduled workflow", runId)
        
        result = await client.get_workflow_result(
            workflow_id=workflow_id,
            run_id=runId
        )
        
        return {
            "result": result,
            "workflow_id": workflow_id,
            "run_id": runId
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Remove Flask-specific run code since FastAPI uses uvicorn
def run_app():
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == '__main__':
    run_app()
