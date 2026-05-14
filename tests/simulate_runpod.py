import urllib.request
import json

def simulate_webhook():
    print("🚀 [RUNPOD SIMULATOR] Packaging meeting data...")
    
    url = "http://127.0.0.1:8000/api/v1/webhook/meet-ended"
    
    # 1. The exact payload structure NERVE expects
    payload = {
        "transcript": """
        Sarah Connor: Alright team, let's get a quick status update. Ayush, what happened with the biometrics DB connection? You said it would be done by Tuesday.
        Ayush Kumar: I'm really sorry, I got completely lost in the Docker configurations and couldn't figure out the environment variables. I'm still working on pulling the embeddings. I will have it pushed by tomorrow evening.
        Sarah Connor: Okay... John, is the FastAPI router ready?
        John Smith: Not yet. I am completely blocked right now because the AWS IAM permissions haven't been granted by DevOps. 
        """,
        "attendees": [
            {"person_id": "P-101", "name": "Ayush Kumar", "role": "AI Developer Intern"},
            {"person_id": "P-102", "name": "Sarah Connor", "role": "Project Manager"},
            {"person_id": "P-103", "name": "John Smith", "role": "Backend Lead"}
        ],
        "metadata": {
            "meeting_id": "M-999-FINAL",
            "project_id": "PROJ-Alpha",
            "security_level": "Internal"
        },
        # NEW: Injecting a memory of a past promise that Ayush missed
        "past_commitments": [
            {
                "commitment_id": "C-001",
                "speaker_id": "P-101",
                "statement": "I will connect the PostgreSQL DB to the biometrics container by Tuesday.",
                "status": "open"
            }
        ]
    }

    # 2. Convert to JSON and set headers
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

    # 3. Fire the webhook!
    print("📡 [RUNPOD SIMULATOR] Firing webhook to NERVE...")
    try:
        response = urllib.request.urlopen(req)
        print(f"✅ [RESPONSE CODE]: {response.getcode()}")
        print(f"✅ [RESPONSE BODY]: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ [ERROR]: {e}")

if __name__ == "__main__":
    simulate_webhook()