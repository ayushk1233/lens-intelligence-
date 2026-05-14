from fastapi import FastAPI
from src.nerve.api.webhook import router as webhook_router

app = FastAPI(title="PULSE NERVE Engine", version="1.0")

# Register our webhook routes
app.include_router(webhook_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "online", "service": "PULSE Intelligence Engine"}