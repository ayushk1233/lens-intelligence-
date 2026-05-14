from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any
from src.lens.graph import lens_app

router = APIRouter()

# 1. Define the exact shape of the data coming from your Meet Recorder Runpod
class MeetPayload(BaseModel):
    transcript: str
    attendees: List[Dict[str, Any]]
    metadata: Dict[str, Any]

def process_meeting(payload: MeetPayload):
    """Background task that runs the LENS LangGraph workflow."""
    print(f"\n⚙️ [NERVE] Processing meeting: {payload.metadata.get('meeting_id')}")
    
    initial_state = {
        "transcript": payload.transcript,
        "attendees": payload.attendees,
        "metadata": payload.metadata
    }
    
    try:
        # Trigger the AI extraction
        final_state = lens_app.invoke(initial_state)
        print("✅ [NERVE] LENS Extraction Complete.")
        
        # TODO in next phase: Route these results to the /warm and /cold folders
        if final_state.get("commitments") and final_state["commitments"].commitments:
            print(f"-> Saved {len(final_state['commitments'].commitments)} Commitments")
        
        if final_state.get("blockers") and final_state["blockers"].blockers:
            print(f"-> Saved {len(final_state['blockers'].blockers)} Blockers")
            
    except Exception as e:
        print(f"❌ [NERVE] Pipeline failed: {e}")

@router.post("/webhook/meet-ended")
async def meet_ended_webhook(payload: MeetPayload, background_tasks: BackgroundTasks):
    """
    Receives the final artifacts from the Meet Recorder.
    Uses BackgroundTasks so the API responds instantly and doesn't timeout.
    """
    # Hand the heavy LLM work to a background thread
    background_tasks.add_task(process_meeting, payload)
    
    return {"status": "accepted", "message": "Meeting payload received. LENS triggered."}