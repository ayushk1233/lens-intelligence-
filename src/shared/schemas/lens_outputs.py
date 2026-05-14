from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import date
from uuid import UUID, uuid4

# --- ENUMS (Restricting LLM Hallucinations) ---

class CommitmentType(str, Enum):
    delivery = "delivery"
    investigation = "investigation"
    approval = "approval"
    followup = "followup"
    escalation = "escalation"

class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class CommitmentStatus(str, Enum):
    open = "open"
    fulfilled = "fulfilled"
    delayed = "delayed"
    abandoned = "abandoned"

class BlockerType(str, Enum):
    dependency = "dependency"
    technical = "technical"
    client = "client"
    resource = "resource"
    comms = "comms"

# --- LAYER 2A: COMMITMENTS ---

class Commitment(BaseModel):
    commitment_id: UUID = Field(default_factory=uuid4, description="Auto-generated UUID")
    speaker_id: str = Field(..., description="Resolved person_id from attendees.json. Required.")
    statement: str = Field(..., description="Exact phrased commitment extracted from transcript")
    commitment_type: CommitmentType
    priority: Priority
    promised_date: Optional[str] = Field(None, description="Extracted or inferred date (YYYY-MM-DD or relative)")
    dependencies: List[str] = Field(default_factory=list, description="List of person_ids this commitment depends on")
    status: CommitmentStatus = Field(default=CommitmentStatus.open)
    owner_explicitly_confirmed: bool = Field(..., description="Did the person explicitly agree? (True) or was it implied? (False)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in extraction (0-1)")
    verified: bool = Field(default=False, description="Human-verified post-extraction")

class CommitmentExtraction(BaseModel):
    """Wrapper to force LLM to output a list of commitments"""
    commitments: List[Commitment]

# --- LAYER 2B: BLOCKERS ---

class Blocker(BaseModel):
    blocker_id: UUID = Field(default_factory=uuid4, description="Auto-generated UUID")
    description: str = Field(..., description="What is blocked and why")
    owner_id: str = Field(..., description="Who owns resolving this blocker (person_id)")
    type: BlockerType
    severity: Priority
    blocking_entity_id: str = Field(..., description="Who or what is being blocked (person_id or project_id)")
    repeat_occurrence: bool = Field(..., description="Has this blocker appeared in prior meetings?")
    escalated: bool = Field(..., description="Has it been escalated to a lead or AM?")
    affected_deliverables: List[str] = Field(default_factory=list, description="What will be delayed if not resolved")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in extraction (0-1)")

class BlockerExtraction(BaseModel):
    """Wrapper to force LLM to output a list of blockers"""
    blockers: List[Blocker]