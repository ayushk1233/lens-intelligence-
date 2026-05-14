import os
import json
from src.shared.schemas.lens_outputs import (
    CommitmentExtraction, BlockerExtraction, DeliveryDrift, ParticipationAnalytics
)

BASE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")

def route_lens_outputs(project_id: str, meeting_id: str, commitments: CommitmentExtraction, blockers: BlockerExtraction, delivery_drift: DeliveryDrift, participation: ParticipationAnalytics, cold_summary_yaml: str):
    
    meeting_dir_warm = os.path.join(BASE_STORAGE_DIR, "projects", project_id, "warm", "meetings", meeting_id)
    os.makedirs(meeting_dir_warm, exist_ok=True)
    
    # 1. Commitments & 2. Blockers (Keep your existing logic for these two)
    if commitments and commitments.commitments:
        with open(os.path.join(meeting_dir_warm, "commitments.json"), "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode='json') for c in commitments.commitments], f, indent=2)
        print("📁 [NERVE ROUTER] Saved Commitments")

    if blockers and blockers.blockers:
        with open(os.path.join(meeting_dir_warm, "blockers.json"), "w", encoding="utf-8") as f:
            json.dump([b.model_dump(mode='json') for b in blockers.blockers], f, indent=2)
        print("📁 [NERVE ROUTER] Saved Blockers")

    # 3. Write Delivery Drift (Layer 2C)
    if delivery_drift:
        with open(os.path.join(meeting_dir_warm, "drift.json"), "w", encoding="utf-8") as f:
            json.dump(delivery_drift.model_dump(mode='json'), f, indent=2)
        print("📁 [NERVE ROUTER] Saved Delivery Drift")

    # 4. Write Participation Analytics (Layer 3C)
    if participation and participation.metrics:
        with open(os.path.join(meeting_dir_warm, "participation.json"), "w", encoding="utf-8") as f:
            json.dump([m.model_dump(mode='json') for m in participation.metrics], f, indent=2)
        print("📁 [NERVE ROUTER] Saved Participation Analytics")

    # 5. Write COLD Summary
    if cold_summary_yaml:
        meeting_dir_cold = os.path.join(BASE_STORAGE_DIR, "projects", project_id, "cold", "meetings", meeting_id)
        os.makedirs(meeting_dir_cold, exist_ok=True)
        with open(os.path.join(meeting_dir_cold, "summary.yaml"), "w", encoding="utf-8") as f:
            f.write(cold_summary_yaml)
        print("📁 [NERVE ROUTER] Saved COLD Summary")