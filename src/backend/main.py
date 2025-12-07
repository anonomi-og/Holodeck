import sys
import os

# Add current directory to path so imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("api")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import traceback

from agent import process_player_action
from tools import get_character_data, get_room_details, execute_query

app = FastAPI(title="Holodeck MVP")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    character_name: str
    session_history: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    narration: str
    out_of_character: Optional[str] = None
    updated_state: Optional[Dict[str, Any]] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Chat request received from {request.character_name}: {request.message}")
    try:
        response_data = process_player_action(
            request.message, 
            request.character_name, 
            request.session_history
        )
        logger.info("Agent processing complete.")
    except Exception as e:
        logger.error(f"Error in chat processing: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get fresh state to return
    state = get_character_data(request.character_name)

    return {
        "narration": response_data.get("narration", ""),
        "out_of_character": response_data.get("out_of_character", ""),
        "updated_state": state
    }

@app.get("/state")
async def get_state(character_name: str):
    state = get_character_data(character_name)
    if "error" in state:
        raise HTTPException(status_code=404, detail=state["error"])
    
    # Enrich with room title if possible
    # (Assuming we store room_id, need to fetch room title)
    if "location_room_id" in state:
        room = execute_query("SELECT title, room_key FROM room WHERE id = ?", (state["location_room_id"],), fetch_one=True)
        if room:
            state["location_title"] = room["title"]
            state["location_key"] = room["room_key"]
    
    return state

@app.get("/health")
async def health_check():
    return {"status": "ok"}
