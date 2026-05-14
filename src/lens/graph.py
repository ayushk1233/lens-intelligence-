import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

# Import schemas, LLM client, and prompts
from src.shared.schemas.lens_outputs import CommitmentExtraction, BlockerExtraction
from src.shared.utils.llm_client import get_structured_llm
from src.lens.prompts import COMMITMENT_EXTRACTION_PROMPT, BLOCKER_EXTRACTION_PROMPT

# --- 1. STATE DEFINITION ---
class LensState(TypedDict):
    """The state object passed through the LENS LangGraph workflow."""
    transcript: str
    attendees: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    commitments: Optional[CommitmentExtraction]
    blockers: Optional[BlockerExtraction]
    cold_summary_yaml: Optional[str]

# --- 2. NODE DEFINITIONS ---
def extract_commitments_node(state: LensState) -> Dict[str, Any]:
    """Node responsible for extracting Layer 2A: Commitments."""
    print("-> LENS Node: Extracting Commitments...")
    
    # 1. Prepare inputs
    transcript = state.get("transcript", "")
    # Dump attendees to JSON string so the LLM can easily read it
    attendees_json = json.dumps(state.get("attendees", []), indent=2)
    
    # 2. Get our resilient LLM bound to the Commitment schema
    llm = get_structured_llm(schema=CommitmentExtraction, model_name="gpt-4o")
    
    # 3. Create and invoke the chain
    chain = COMMITMENT_EXTRACTION_PROMPT | llm
    
    try:
        result = chain.invoke({
            "transcript": transcript,
            "attendees_json": attendees_json
        })
        return {"commitments": result}
    except Exception as e:
        print(f"[ERROR] Failed to extract commitments: {e}")
        return {"commitments": None}


def extract_blockers_node(state: LensState) -> Dict[str, Any]:
    """Node responsible for extracting Layer 2B: Blockers."""
    print("-> LENS Node: Extracting Blockers...")
    
    # 1. Prepare inputs
    transcript = state.get("transcript", "")
    attendees_json = json.dumps(state.get("attendees", []), indent=2)
    
    # 2. Get our resilient LLM bound to the Blocker schema
    llm = get_structured_llm(schema=BlockerExtraction, model_name="gpt-4o")
    
    # 3. Create and invoke the chain
    chain = BLOCKER_EXTRACTION_PROMPT | llm
    
    try:
        result = chain.invoke({
            "transcript": transcript,
            "attendees_json": attendees_json
        })
        return {"blockers": result}
    except Exception as e:
        print(f"[ERROR] Failed to extract blockers: {e}")
        return {"blockers": None}

# --- 3. GRAPH COMPILATION ---
def build_lens_graph():
    """Builds and compiles the LENS state graph."""
    workflow = StateGraph(LensState)
    
    workflow.add_node("extract_commitments", extract_commitments_node)
    workflow.add_node("extract_blockers", extract_blockers_node)
    
    workflow.set_entry_point("extract_commitments")
    workflow.add_edge("extract_commitments", "extract_blockers")
    workflow.add_edge("extract_blockers", END)
    
    return workflow.compile()

# Initialize the compiled graph for imports
lens_app = build_lens_graph()