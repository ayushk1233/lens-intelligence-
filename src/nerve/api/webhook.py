from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any
from src.lens.graph import lens_app
from src.nerve.routers.file_router import route_lens_outputs # <--- IMPORT ADDED

router = APIRouter()

class MeetPayload(BaseModel):
    transcript: str
    attendees: List[Dict[str, Any]]
    metadata: Dict[str, Any]

def process_meeting(payload: MeetPayload):
    """Background task that runs LENS and routes the output."""
    project_id = payload.metadata.get('project_id', 'UNKNOWN_PROJECT')
    meeting_id = payload.metadata.get('meeting_id', 'UNKNOWN_MEET')
    
    print(f"\n⚙️ [NERVE] Processing meeting: {meeting_id} for {project_id}")
    
    initial_state = {
        "transcript": payload.transcript,
        "attendees": payload.attendees,
        "metadata": payload.metadata
    }
    
    try:
        final_state = lens_app.invoke(initial_state)
        print("✅ [NERVE] LENS Extraction Complete.")
        
        # --- NEW: ROUTE FILES TO DISK ---
        route_lens_outputs(
            project_id=project_id,
            meeting_id=meeting_id,
            commitments=final_state.get("commitments"),
            blockers=final_state.get("blockers"),
            cold_summary_yaml=final_state.get("cold_summary_yaml")
        )
            
    except Exception as e:
        print(f"❌ [NERVE] Pipeline failed: {e}")

# ... (Keep your existing @router.post("/webhook/meet-ended") exactly the same below this)
@router.post("/webhook/meet-ended")
async def meet_ended_webhook(payload: MeetPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_meeting, payload)
    return {"status": "accepted", "message": "Meeting payload received. LENS triggered."}