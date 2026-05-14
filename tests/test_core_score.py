import sys
import os

# Ensure the project root is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.graph import core_app

def run_final_test():
    print("🎯 [CORE TEST] Generating Final Project Health Report...\n")
    final_state = core_app.invoke({"project_id": "PROJ-Alpha"})
    report = final_state["report"]

    print(f"--- OVERALL SCORE: {report.overall_score}/100 ---")
    print(f"\n{report.executive_summary}\n")
    print("--- DIMENSION BREAKDOWN ---")
    for dim in report.dimensions:
        print(f"[{dim.score}/10] {dim.dimension_name}: {dim.justification}")
    
    if report.critical_risks:
        print("\n⚠️ CRITICAL RISKS:")
        for risk in report.critical_risks:
            print(f"- {risk}")

if __name__ == "__main__":
    run_final_test()