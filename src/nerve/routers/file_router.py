import os
import json
from datetime import datetime
from src.shared.schemas.lens_outputs import CommitmentExtraction, BlockerExtraction

# In production, this would be an S3 bucket or mounted K8s volume. 
# For now, we use a local 'data' directory at the root of the repo.
BASE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")

def route_lens_outputs(project_id: str, meeting_id: str, commitments: CommitmentExtraction, blockers: BlockerExtraction):
    """
    Routes the extracted LENS intelligence to the correct physical directories.
    Following PULSE rules: Primary storage axis is project_id.
    """
    
    # 1. Define the physical paths
    # e.g., data/projects/PROJ-Alpha/warm/meetings/M-999-FINAL/
    meeting_dir = os.path.join(BASE_STORAGE_DIR, "projects", project_id, "warm", "meetings", meeting_id)
    
    # Ensure directories exist
    os.makedirs(meeting_dir, exist_ok=True)
    
    # 2. Write Commitments to disk (Layer 2A)
    if commitments and commitments.commitments:
        commitments_path = os.path.join(meeting_dir, "commitments.json")
        with open(commitments_path, "w", encoding="utf-8") as f:
            # Pydantic's model_dump() cleanly converts to dicts
            json.dump([c.model_dump(mode='json') for c in commitments.commitments], f, indent=2)
        print(f"📁 [NERVE ROUTER] Saved Commitments to {commitments_path}")

    # 3. Write Blockers to disk (Layer 2B)
    if blockers and blockers.blockers:
        blockers_path = os.path.join(meeting_dir, "blockers.json")
        with open(blockers_path, "w", encoding="utf-8") as f:
            json.dump([b.model_dump(mode='json') for b in blockers.blockers], f, indent=2)
        print(f"📁 [NERVE ROUTER] Saved Blockers to {blockers_path}")