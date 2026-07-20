from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Incident
from app.schemas import (
    AnalyzeIncidentRequest,
    AnalyzeIncidentResponse,
    HealthResponse,
    IncidentResponse,
    SqlCheckRequest,
    SqlCheckResponse,
)
from app.services.incident_service import IncidentService
from app.services.sql_safety import check_read_only_sql


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DE Support Agent",
    version="1.0.0",
    description=(
        "AI-помощник первой линии поддержки Data Engineering: "
        "анализирует логи, ищет решения в базе знаний и сохраняет инциденты."
    ),
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/api/v1/incidents/analyze",
    response_model=AnalyzeIncidentResponse,
    tags=["incidents"],
)
def analyze_incident(
    payload: AnalyzeIncidentRequest,
    db: Session = Depends(get_db),
) -> AnalyzeIncidentResponse:
    service = IncidentService(db)
    return service.analyze_and_save(payload)


@app.get(
    "/api/v1/incidents/{incident_id}",
    response_model=IncidentResponse,
    tags=["incidents"],
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
) -> IncidentResponse:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)


@app.post(
    "/api/v1/tools/sql-check",
    response_model=SqlCheckResponse,
    tags=["tools"],
)
def sql_check(payload: SqlCheckRequest) -> SqlCheckResponse:
    result = check_read_only_sql(payload.query)
    return SqlCheckResponse(**result)
