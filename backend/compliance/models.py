from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ComplianceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid4()))
    regulation_id: str
    relevance_score: float
    impacted_business_tags: list[str]
    impacted_documents: list[str]
    risk_level: str
    recommended_actions: list[str]
    owner_role: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

