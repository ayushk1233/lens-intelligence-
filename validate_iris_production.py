import os
import json
import yaml
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# 1. GENERATE REALISTIC & NOISY MOCK DATA
# ==========================================

project_id = "PROJ-Titan"
meeting_id = "M-20260515-SYNC"

# Mock 1: metadata.json (With realistic noise, biometrics, and updated timezone syntax)
mock_metadata = {
    "meeting_id": meeting_id,
    "project_id": project_id,
    "security_level": "Internal",
    "timestamp": datetime.now(timezone.utc).isoformat(), # FIXED: Deprecation Warning
    "duration_seconds": 1845,
    "agenda_tags": ["sprint_blockers", "aws_migration"],
    "transcript_status": "completed",
    "biometric_forensics": {
        "SPEAKER_04": {"status": "REJECTED_LOW_CONFIDENCE", "top_match": "Sanket", "score": 0.61}
    }
}

# Mock 2: attendees.json (Diverse roles, including an unmapped/external person)
mock_attendees = [
    {"person_id": "P-201", "name": "Riya Sharma", "role": "Product Manager", "dept": "Product"},
    {"person_id": "P-202", "name": "David Chen", "role": "DevOps Engineer", "dept": "Infrastructure"},
    {"person_id": "P-203", "name": "Kabir Singh", "role": "Frontend Lead", "dept": "Engineering"},
    {"person_id": "UNKNOWN_01", "name": "Unknown Caller", "role": "Guest", "dept": None} # FIXED: null -> None
]

# Mock 3: transcript.txt (Noisy, Hinglish, cross-talk, late joiners)
mock_transcript = """
[00:00:12] Riya Sharma: Okay, let's start. Kabir, where are we with the frontend dashboard?
[00:00:15] Unknown Caller: Hey guys, sorry I'm late, my audio was completely messed up. Can you hear me?
[00:00:18] Riya Sharma: Yeah, we hear you. No problem. Kabir, go ahead.
[00:00:20] Kabir Singh: Yeah, so... um, the UI is mostly done, but the staging API is constantly throwing 500s. Matlab, data load hi nahi ho raha hai. I can't test the components. I am completely blocked right now.
[00:00:35] David Chen: Ah, my bad guys. That's the AWS IAM role migration we did last night. I think I missed a policy attachment for the staging DB. 
[00:00:42] Riya Sharma: How long to fix?
[00:00:44] David Chen: I will patch the IAM permissions and restart the ECS cluster by 3 PM today.
[00:00:50] Riya Sharma: Okay, decision made: we push the UAT demo to Friday to give us a buffer. David, please get that patched ASAP. Kabir, just work on the local mock data until staging is back up.
[00:01:05] Kabir Singh: Sounds good.
"""

# ==========================================
# 2. SIMULATE R2 STORAGE CO-LOCATION
# ==========================================

R2_BUCKET_LOCAL = "data" # Using your actual local data directory
meeting_dir = os.path.join(R2_BUCKET_LOCAL, "projects", project_id, "meetings", meeting_id)

print(f"📦 [STORAGE] Creating R2 project hierarchy at: {meeting_dir}")
os.makedirs(meeting_dir, exist_ok=True)

with open(os.path.join(meeting_dir, "metadata.json"), "w") as f:
    json.dump(mock_metadata, f, indent=2)

with open(os.path.join(meeting_dir, "attendees.json"), "w") as f:
    json.dump(mock_attendees, f, indent=2)

with open(os.path.join(meeting_dir, "transcript.txt"), "w") as f:
    f.write(mock_transcript.strip())

# ==========================================
# 3. DEFINE STRICT IRIS YAML SCHEMAS
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

# ==========================================
# 4. EXECUTE IRIS AGENT
# ==========================================

def execute_iris():
    print("\n👁️  [IRIS] Waking up. Ingesting Meeting Context...")
    
    with open(os.path.join(meeting_dir, "metadata.json"), "r") as f:
        meta = json.load(f)
    with open(os.path.join(meeting_dir, "attendees.json"), "r") as f:
        attendees = json.load(f)
    with open(os.path.join(meeting_dir, "transcript.txt"), "r") as f:
        transcript = f.read()

    print("🧠 [IRIS] Processing transcript (Filtering noise, mapping IDs...)")
    
    simulated_llm_output = IrisYamlSchema(
        decisions=["Push the UAT demo to Friday."],
        action_items=[
            ActionItem(owner_id="P-202", task="Patch AWS IAM permissions and restart ECS cluster.", deadline="Today 3 PM"),
            ActionItem(owner_id="P-203", task="Work on local mock data.", deadline=None)
        ],
        blockers=[
            Blocker(owner_id="P-203", issue="Staging API returning 500 errors due to AWS IAM.")
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
    
    print(f"✅ [IRIS] SUCCESS: Generated <85 token summary.yaml")
    print(f"📁 [STORAGE] Saved to co-located directory: {yaml_path}")
    print("\n--- GENERATED YAML ---")
    print(yaml_content)

if __name__ == "__main__":
    execute_iris()