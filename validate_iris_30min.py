import os
import json
import yaml
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# 1. THE 30-MINUTE RAW GPU TRANSCRIPT
# ==========================================
# Simulating the raw output from your Whisper/Pyannote pipeline.
# Notice the timestamps span from 0 seconds to 1795 seconds (~30 mins).
runpod_raw_transcript = [
    {"start": 10.5, "end": 15.2, "speaker": "SPEAKER_01", "text": "Alright, is everyone here? Can you guys hear me?"},
    {"start": 15.5, "end": 18.0, "speaker": "SPEAKER_02", "text": "Yeah, I can hear you. Kabir is still joining I think."},
    {"start": 18.5, "end": 25.0, "speaker": "SPEAKER_03", "text": "Sorry guys, my Zoom crashed. I am here now. Let's get started."},
    {"start": 26.0, "end": 45.0, "speaker": "SPEAKER_01", "text": "Okay, agenda for today is the architecture migration and the biometrics integration. Let's start with the database migration. David, where are we with moving the PostgreSQL instances to the new VPC?"},
    {"start": 46.0, "end": 120.0, "speaker": "SPEAKER_02", "text": "It's been a nightmare, honestly. The AWS Terraform scripts applied fine, but the security groups are blocking inbound traffic from the Kubernetes cluster. I spent three hours yesterday just trying to ping the DB from the pods. I opened a ticket with CloudOps but they haven't responded."},
    {"start": 121.0, "end": 135.0, "speaker": "SPEAKER_01", "text": "Okay, that's a massive blocker. If the DB isn't up, Ayush can't test the voice embeddings. I will escalate the CloudOps ticket to the Director right after this call."},
    {"start": 136.0, "end": 140.0, "speaker": "SPEAKER_02", "text": "Thanks, Sarah. Once they unblock the port, the migration will take like two hours."},
    {"start": 600.0, "end": 645.0, "speaker": "SPEAKER_04", "text": "Hey guys, quick question about the frontend. Are we still using EasyOCR for the video processing, or did we officially rip that out?"},
    {"start": 646.0, "end": 680.0, "speaker": "SPEAKER_03", "text": "We completely ripped it out. The PR was merged last night. It was way too brittle. We are moving strictly to the Calendar API pre-fill and the audio biometrics for speaker mapping. It makes the UI much cleaner anyway."},
    {"start": 681.0, "end": 690.0, "speaker": "SPEAKER_01", "text": "Great decision. So, decision officially logged: EasyOCR is deprecated. We rely solely on voice biometrics."},
    {"start": 1200.0, "end": 1250.0, "speaker": "SPEAKER_04", "text": "So regarding the biometric mapping, I've got the embedding model working locally. The ECAPA-TDNN model from SpeechBrain is giving us like 95% accuracy on clean audio. But I don't have anywhere to store the vector embeddings yet because, well, the database is blocked."},
    {"start": 1251.0, "end": 1300.0, "speaker": "SPEAKER_01", "text": "Understood. Ayush, for now, just mock the database locally using SQLite so you don't lose momentum. Once David's CloudOps ticket is resolved, you can port it over to the remote PostgreSQL."},
    {"start": 1301.0, "end": 1315.0, "speaker": "SPEAKER_04", "text": "Makes sense. I'll build the local SQLite mock by tomorrow morning."},
    {"start": 1780.0, "end": 1788.0, "speaker": "SPEAKER_01", "text": "Alright, we are at time. Thanks everyone, I'll send out the notes and push that escalation. Bye."},
    {"start": 1789.0, "end": 1795.0, "speaker": "SPEAKER_02", "text": "Catch you later."}
]

# ==========================================
# 2. SIMULATE FORM METADATA & ATTENDEES
# ==========================================
project_id = "PROJ-CoreArch"
meeting_id = "M-30MIN-STRESS-TEST"

# The biometric map that links the GPU output to your actual database IDs
biometric_map = {
    "SPEAKER_01": "P-101", # Sarah (PM)
    "SPEAKER_02": "P-102", # David (DevOps)
    "SPEAKER_03": "P-103", # Kabir (Frontend)
    "SPEAKER_04": "P-104", # Ayush (AI)
}

mock_attendees = [
    {"person_id": "P-101", "name": "Sarah Connor", "role": "Project Manager"},
    {"person_id": "P-102", "name": "David Chen", "role": "DevOps Engineer"},
    {"person_id": "P-103", "name": "Kabir Singh", "role": "Frontend Lead"},
    {"person_id": "P-104", "name": "Ayush Kumar", "role": "AI Engineer"}
]

mock_metadata = {
    "meeting_id": meeting_id,
    "project_id": project_id,
    "security_level": "Internal",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "duration_seconds": 1800, # 30 minutes
    "agenda_tags": ["architecture", "migration", "biometrics"],
    "transcript_status": "completed"
}

# ==========================================
# 3. BUILD THE TRANSCRIPT & R2 FOLDER
# ==========================================
formatted_transcript_lines = []
for chunk in runpod_raw_transcript:
    mins, secs = divmod(int(chunk["start"]), 60)
    timestamp = f"[{mins:02d}:{secs:02d}]"
    
    # Map SPEAKER_XX to actual name using the biometric map
    person_id = biometric_map.get(chunk["speaker"], "UNKNOWN")
    speaker_name = next((p["name"] for p in mock_attendees if p["person_id"] == person_id), chunk["speaker"])
    
    formatted_transcript_lines.append(f"{timestamp} {speaker_name}: {chunk['text'].strip()}")

final_transcript_text = "\n".join(formatted_transcript_lines)

R2_BUCKET_LOCAL = "data"
meeting_dir = os.path.join(R2_BUCKET_LOCAL, "projects", project_id, "meetings", meeting_id)

print(f"📦 [STORAGE] Creating R2 project hierarchy at: {meeting_dir}")
os.makedirs(meeting_dir, exist_ok=True)

with open(os.path.join(meeting_dir, "metadata.json"), "w") as f: json.dump(mock_metadata, f, indent=2)
with open(os.path.join(meeting_dir, "attendees.json"), "w") as f: json.dump(mock_attendees, f, indent=2)
with open(os.path.join(meeting_dir, "transcript.txt"), "w") as f: f.write(final_transcript_text)


# ==========================================
# 4. EXECUTE IRIS COMPRESSION AGENT
# ==========================================
class ActionItem(BaseModel):
    owner_id: str = Field(..., description="The exact person_id from attendees.json.")
    task: str = Field(..., description="Max 10 words. What needs to be done.")
    deadline: Optional[str] = Field(None, description="When it is due, if mentioned.")

class Blocker(BaseModel):
    owner_id: str = Field(..., description="The person_id blocked.")
    issue: str = Field(..., description="Max 10 words. The technical or business hurdle.")

class IrisYamlSchema(BaseModel):
    decisions: List[str] = Field(..., description="List of final decisions made. Max 10 words each.")
    action_items: List[ActionItem] = Field(default_factory=list)
    blockers: List[Blocker] = Field(default_factory=list)

def execute_iris():
    print("👁️  [IRIS] Waking up. Ingesting 30-Minute Meeting Context...")
    
    # SIMULATING THE LLM COMPRESSION
    # Notice how it ignores the first 5 minutes of "can you hear me"
    # It strictly extracts the business value mapped to IDs
    simulated_llm_output = IrisYamlSchema(
        decisions=[
            "EasyOCR is officially deprecated in favor of voice biometrics."
        ],
        action_items=[
            ActionItem(owner_id="P-101", task="Escalate CloudOps ticket to unblock database port.", deadline="Today"),
            ActionItem(owner_id="P-104", task="Build local SQLite mock for embedding storage.", deadline="Tomorrow morning")
        ],
        blockers=[
            Blocker(owner_id="P-102", issue="AWS security groups blocking inbound K8s traffic to database."),
            Blocker(owner_id="P-104", issue="Cannot test biometrics remote storage until DB is unblocked.")
        ]
    )

    yaml_content = yaml.dump(
        simulated_llm_output.model_dump(exclude_unset=True, exclude_none=True), 
        sort_keys=False, 
        default_flow_style=False
    )

    yaml_path = os.path.join(meeting_dir, "summary.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    
    print(f"✅ [IRIS] SUCCESS: Compressed 30-min meeting into <85 token YAML.")
    print(f"📁 [STORAGE] Saved to co-located directory: {yaml_path}")
    print("\n--- RAW TRANSCRIPT GENERATED FROM RUNPOD (Snippet) ---")
    print("\n".join(final_transcript_text.split("\n")[:5]) + "\n... (continues for 30 mins) ...")
    print("\n--- FINAL IRIS YAML COMPRESSION ---")
    print(yaml_content)

if __name__ == "__main__":
    execute_iris()