import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from src.shared.schemas.core_outputs import ProjectHealthReport
from src.core.prompts import CORE_SCORING_PROMPT
from src.shared.utils.llm_client import get_structured_llm

# --- 1. STATE DEFINITION ---
class CoreState(TypedDict):
    project_id: str
    raw_context: str
    report: ProjectHealthReport

# --- 2. NODE DEFINITIONS ---
def context_loader_node(state: CoreState) -> Dict[str, Any]:
    """Scans the file system based on the project_index and builds the LLM context."""
    project_id = state["project_id"]
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "projects", project_id)
    index_path = os.path.join(base_path, "project_index.json")
    
    if not os.path.exists(index_path):
        return {"raw_context": "ERROR: Project index not found."}

    with open(index_path, "r") as f:
        index = json.load(f)

    full_context = f"PROJECT: {project_id}\nLAST SWEEP: {index['last_sweep']}\n\n"
    
    # Iterate through logged meetings to gather intelligence
    for meeting_id in index.get("meetings_logged", []):
        full_context += f"--- MEETING: {meeting_id} ---\n"
        
        # Load COLD Summary
        summary_path = os.path.join(base_path, "cold", "meetings", meeting_id, "summary.yaml")
        if os.path.exists(summary_path):
            with open(summary_path, "r") as f:
                full_context += f"SUMMARY:\n{f.read()}\n"
        
        # Load WARM Data (Blockers & Drift)
        for file_name in ["blockers.json", "drift.json"]:
            path = os.path.join(base_path, "warm", "meetings", meeting_id, file_name)
            if os.path.exists(path):
                with open(path, "r") as f:
                    full_context += f"{file_name.upper()}:\n{f.read()}\n"
    
    return {"raw_context": full_context}

def health_scorer_node(state: CoreState) -> Dict[str, Any]:
    """Invokes the LLM to generate the ProjectHealthReport."""
    print(f"📊 [CORE] Scoring health for {state['project_id']}...")
    
    llm = get_structured_llm(schema=ProjectHealthReport, model_name="gpt-4o-mini")
    chain = CORE_SCORING_PROMPT | llm
    
    report = chain.invoke({"project_data": state["raw_context"]})
    return {"report": report}

# --- 3. GRAPH COMPILATION ---
def build_core_graph():
    workflow = StateGraph(CoreState)
    workflow.add_node("load_context", context_loader_node)
    workflow.add_node("score_health", health_scorer_node)
    
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "score_health")
    workflow.add_edge("score_health", END)
    
    return workflow.compile()

core_app = build_core_graph()