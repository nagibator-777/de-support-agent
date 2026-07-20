from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str


class AnalyzeIncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    log: str = Field(min_length=5, max_length=30_000)
    context: str | None = Field(default=None, max_length=5_000)
    use_llm: bool = True


class AnalyzeIncidentResponse(BaseModel):
    incident_id: int
    category: str
    severity: str
    summary: str
    probable_causes: list[str]
    recommended_actions: list[str]
    matched_rules: list[str]
    sources: list[str]
    llm_used: bool


class IncidentResponse(BaseModel):
    id: int
    title: str
    log: str
    category: str
    severity: str
    summary: str
    probable_causes_json: str
    actions_json: str
    sources_json: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SqlCheckRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)


class SqlCheckResponse(BaseModel):
    allowed: bool
    reason: str
    normalized_query: str
