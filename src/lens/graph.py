import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

# Import all schemas
from src.shared.schemas.lens_outputs import (
    CommitmentExtraction, BlockerExtraction, ColdSummary, 
    DeliveryDrift, ParticipationAnalytics
)
from src.shared.utils.llm_client import get_structured_llm

# Import all prompts
from src.lens.prompts import (
    COMMITMENT_EXTRACTION_PROMPT, BLOCKER_EXTRACTION_PROMPT, YAML_SUMMARY_PROMPT,
    DELIVERY_DRIFT_PROMPT, PARTICIPATION_PROMPT
)

# --- 1. STATE DEFINITION ---
class LensState(TypedDict):
    """The complete state object passed through the LENS workflow."""
    # INPUTS
    transcript: str
    attendees: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    past_commitments: List[Dict[str, Any]] # NEW: Memory for drift calculation
    
    # OUTPUTS
    commitments: Optional[CommitmentExtraction]
    blockers: Optional[BlockerExtraction]
    delivery_drift: Optional[DeliveryDrift] # NEW
    participation: Optional[ParticipationAnalytics] # NEW
    cold_summary_yaml: Optional[str]

# --- 2. NODE DEFINITIONS ---
# (Keep existing commitments and blockers nodes exactly the same)
def extract_commitments_node(state: LensState) -> Dict[str, Any]:
    print("-> LENS Node: Extracting Commitments...")
    llm = get_structured_llm(schema=CommitmentExtraction, model_name="gpt-4o-mini")
    chain = COMMITMENT_EXTRACTION_PROMPT | llm
    try:
        result = chain.invoke({"transcript": state.get("transcript", ""), "attendees_json": json.dumps(state.get("attendees", []), indent=2)})
        return {"commitments": result}
    except Exception as e:
        print(f"[ERROR] Commitments: {e}")
        return {"commitments": None}

def extract_blockers_node(state: LensState) -> Dict[str, Any]:
    print("-> LENS Node: Extracting Blockers...")
    llm = get_structured_llm(schema=BlockerExtraction, model_name="gpt-4o-mini")
    chain = BLOCKER_EXTRACTION_PROMPT | llm
    try:
        result = chain.invoke({"transcript": state.get("transcript", ""), "attendees_json": json.dumps(state.get("attendees", []), indent=2)})
        return {"blockers": result}
    except Exception as e:
        print(f"[ERROR] Blockers: {e}")
        return {"blockers": None}

# --- NEW: PHASE 2 (DELIVERY DRIFT) ---
def calculate_drift_node(state: LensState) -> Dict[str, Any]:
    print("-> LENS Node: Calculating Delivery Drift...")
    past_commitments = state.get("past_commitments", [])
    
    # If this is the first meeting ever, there is no drift to calculate
    if not past_commitments:
        print("   [INFO] No past commitments found. Skipping drift calculation.")
        return {"delivery_drift": None}
        
    llm = get_structured_llm(schema=DeliveryDrift, model_name="gpt-4o-mini")
    chain = DELIVERY_DRIFT_PROMPT | llm
    try:
        result = chain.invoke({
            "transcript": state.get("transcript", ""),
            "attendees_json": json.dumps(state.get("attendees", []), indent=2),
            "past_commitments_json": json.dumps(past_commitments, indent=2)
        })
        return {"delivery_drift": result}
    except Exception as e:
        print(f"[ERROR] Delivery Drift: {e}")
        return {"delivery_drift": None}

# --- NEW: PHASE 3 (PARTICIPATION ANALYTICS) ---
def analyze_participation_node(state: LensState) -> Dict[str, Any]:
    print("-> LENS Node: Analyzing Participation...")
    llm = get_structured_llm(schema=ParticipationAnalytics, model_name="gpt-4o-mini")
    chain = PARTICIPATION_PROMPT | llm
    try:
        result = chain.invoke({"transcript": state.get("transcript", ""), "attendees_json": json.dumps(state.get("attendees", []), indent=2)})
        return {"participation": result}
    except Exception as e:
        print(f"[ERROR] Participation: {e}")
        return {"participation": None}

# (Keep existing summary node)
def generate_summary_node(state: LensState) -> Dict[str, Any]:
    print("-> LENS Node: Generating COLD Summary...")
    llm = get_structured_llm(schema=ColdSummary, model_name="gpt-4o-mini")
    chain = YAML_SUMMARY_PROMPT | llm
    try:
        result = chain.invoke({"transcript": state.get("transcript", ""), "attendees_json": json.dumps(state.get("attendees", []), indent=2)})
        return {"cold_summary_yaml": result.yaml_content}
    except Exception as e:
        print(f"[ERROR] COLD Summary: {e}")
        return {"cold_summary_yaml": None}

# --- 3. GRAPH COMPILATION ---
def build_lens_graph():
    workflow = StateGraph(LensState)
    
    # Add all 5 nodes
    workflow.add_node("extract_commitments", extract_commitments_node)
    workflow.add_node("extract_blockers", extract_blockers_node)
    workflow.add_node("calculate_drift", calculate_drift_node)
    workflow.add_node("analyze_participation", analyze_participation_node)
    workflow.add_node("generate_summary", generate_summary_node)
    
    # Define the sequential execution path
    workflow.set_entry_point("extract_commitments")
    workflow.add_edge("extract_commitments", "extract_blockers")
    workflow.add_edge("extract_blockers", "calculate_drift")
    workflow.add_edge("calculate_drift", "analyze_participation")
    workflow.add_edge("analyze_participation", "generate_summary")
    workflow.add_edge("generate_summary", END)
    
    return workflow.compile()

lens_app = build_lens_graph()