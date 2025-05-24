from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json # Added
import uvicorn

app = FastAPI()

STORY_STATE_FILE = "story_state.json"

# Create static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serves the main HTML page."""
    html_path = 'static/index.html'
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="index.html not found. Make sure it exists in the 'static' directory.")
    return FileResponse(html_path)

@app.get("/story_data")
async def get_story_data():
    """Returns the current story state from the JSON file."""
    if not os.path.exists(STORY_STATE_FILE):
        return JSONResponse(content={"error": "Story state not found. Run main.py first."}, status_code=200) # Return 200 so frontend can handle it
    try:
        with open(STORY_STATE_FILE, 'r') as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except json.JSONDecodeError:
         return JSONResponse(content={"error": "Story state file is corrupted or being written."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading story state: {e}")

# Add this to run directly if needed
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)