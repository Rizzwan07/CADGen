import os
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from generator import generate_cad

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str
    session_id: str | None = None

@app.post("/generate")
def generate(request: PromptRequest):
    result = generate_cad(request.prompt, request.session_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(tempfile.gettempdir(), "cadgen", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    if filename.endswith(".step"):
        media_type = "application/step"
    elif filename.endswith(".dxf"):
        media_type = "application/dxf"
    else:
        media_type = "model/stl"
    return FileResponse(path, media_type=media_type, filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
