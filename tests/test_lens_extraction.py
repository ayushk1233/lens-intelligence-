import sys
import os

# Ensure the 'src' directory is in the Python path for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lens.graph import lens_app

def run_test():
    print("🚀 Starting LENS Extraction Test...\n")

    # 1. Mock the Layer 0 Inputs (Attendees)
    mock_attendees = [
        {"person_id": "P-101", "name": "Ayush Kumar", "role": "AI Developer Intern"},
        {"person_id": "P-102", "name": "Sarah Connor", "role": "Project Manager"},
        {"person_id": "P-103", "name": "John Smith", "role": "Backend Lead"}
    ]

    # 2. Mock the Layer 0 Inputs (Transcript)
    # Notice how we explicitly have Ayush make a promise, and John state a blocker.
    mock_transcript = """
    Sarah Connor: Alright team, let's get a quick status update on the new Meet orchestration pipeline. Ayush, where are we with the biometrics integration?
    Ayush Kumar: I'm still working on pulling the embeddings from the secure DB. I will have the DB connection script pushed and tested by tomorrow evening.
    Sarah Connor: Great, I'll mark that down. John, is the FastAPI router ready?
    John Smith: Not yet. I am completely blocked right now because the AWS IAM permissions haven't been granted by DevOps. I can't deploy the container until they approve the request. It's delaying the entire staging release.
    Sarah Connor: Okay, I will escalate that to DevOps right after this call.
    """

    # 3. Construct the Initial State
    initial_state = {
        "transcript": mock_transcript,
        "attendees": mock_attendees,
        "metadata": {"meeting_id": "M-999", "project_id": "PROJ-Alpha"}
    }

    # 4. Invoke the LangGraph Agent
    print("⏳ Invoking LENS Graph...\n")
    final_state = lens_app.invoke(initial_state)

    # 5. Print the Results
    print("✅ EXTRACTION COMPLETE\n")
    
    print("--- COMMITMENTS ---")
    if final_state.get("commitments") and final_state["commitments"].commitments:
        for c in final_state["commitments"].commitments:
            # Pydantic's model_dump_json gives us a clean string
            print(c.model_dump_json(indent=2))
    else:
        print("No commitments extracted or extraction failed.")

    print("\n--- BLOCKERS ---")
    if final_state.get("blockers") and final_state["blockers"].blockers:
        for b in final_state["blockers"].blockers:
            print(b.model_dump_json(indent=2))
    else:
        print("No blockers extracted or extraction failed.")

if __name__ == "__main__":
    run_test()