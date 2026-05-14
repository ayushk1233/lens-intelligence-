from pydantic import BaseModel, Field
from typing import List

class DimensionScore(BaseModel):
    dimension_name: str = Field(..., description="e.g., 'Velocity', 'Blocker Severity', 'Team Alignment'")
    score: int = Field(..., ge=1, le=10, description="Score from 1 (Failing) to 10 (Perfect).")
    justification: str = Field(..., description="One sentence explaining the score using strict evidence from the data.")

class ProjectHealthReport(BaseModel):
    overall_score: int = Field(..., ge=1, le=100, description="Aggregate health score from 1-100.")
    executive_summary: str = Field(..., description="A harsh, objective 2-paragraph markdown summary of the project state.")
    dimensions: List[DimensionScore] = Field(..., description="Scores for at least 3 distinct project dimensions.")
    critical_risks: List[str] = Field(..., description="Bullet points of immediate threats to delivery. Empty if none.")