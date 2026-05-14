import os
import json
from datetime import datetime

# Pointing to our central data directory
BASE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")

def run_nightly_sweep(project_id: str):
    """
    Simulates a nightly cron job.
    1. Ages open blockers.
    2. Compiles a central index of all recorded meetings for the CORE agent.
    """
    print(f"🌙 [NERVE CRON] Waking up. Starting nightly sweep for {project_id}...")
    
    project_dir = os.path.join(BASE_STORAGE_DIR, "projects", project_id)
    warm_meetings_dir = os.path.join(project_dir, "warm", "meetings")
    
    if not os.path.exists(warm_meetings_dir):
        print("   [INFO] No meetings found. Going back to sleep.")
        return

    total_blockers_aged = 0
    meeting_index = []

    # 1. Iterate through all meetings in the WARM folder
    for meeting_id in os.listdir(warm_meetings_dir):
        # Ignore hidden files like .DS_Store on macOS
        if meeting_id.startswith('.'): continue
        
        meeting_path = os.path.join(warm_meetings_dir, meeting_id)
        if not os.path.isdir(meeting_path): continue
        
        # Add to our central index
        meeting_index.append(meeting_id)

        # 2. Age the blockers
        blockers_file = os.path.join(meeting_path, "blockers.json")
        if os.path.exists(blockers_file):
            with open(blockers_file, "r") as f:
                blockers = json.load(f)
            
            updated = False
            for b in blockers:
                # If the blocker isn't explicitly marked 'resolved', age it.
                if b.get("status", "open") != "resolved":
                    b["days_open"] = b.get("days_open", 0) + 1
                    updated = True
                    total_blockers_aged += 1
            
            # Save the aged blockers back to disk
            if updated:
                with open(blockers_file, "w") as f:
                    json.dump(blockers, f, indent=2)
    
    # 3. Write the Master Project Index
    # CORE will read this file to know exactly what folders to look inside
    index_path = os.path.join(project_dir, "project_index.json")
    with open(index_path, "w") as f:
        json.dump({
            "project_id": project_id,
            "last_sweep": datetime.now().isoformat(),
            "meetings_logged": meeting_index
        }, f, indent=2)
        
    print(f"✅ [NERVE CRON] Sweep complete. Aged {total_blockers_aged} blockers.")
    print(f"📁 [NERVE CRON] Generated Master Index at: {index_path}")

if __name__ == "__main__":
    # Simulate the cron job running for our test project
    run_nightly_sweep("PROJ-Alpha")