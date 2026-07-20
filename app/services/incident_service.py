import json

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Incident
from app.schemas import AnalyzeIncidentRequest, AnalyzeIncidentResponse
from app.services.analyzer import analyze_log
from app.services.knowledge import KnowledgeBase
from app.services.llm import GigaChatEnhancer


class IncidentService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.knowledge = KnowledgeBase(self.settings.knowledge_base_path)
        self.llm = GigaChatEnhancer()

    def analyze_and_save(
        self,
        payload: AnalyzeIncidentRequest,
    ) -> AnalyzeIncidentResponse:
        analysis = analyze_log(payload.log)
        query = " ".join(
            [
                payload.title,
                payload.log,
                payload.context or "",
                analysis["category"],
                " ".join(analysis["matched_rules"]),
            ]
        )
        documents = self.knowledge.search(query)
        sources = [document["title"] for document in documents]

        llm_summary = None
        if payload.use_llm:
            llm_summary = self.llm.enhance(
                title=payload.title,
                log=payload.log,
                analysis=analysis,
                sources=documents,
            )

        summary = llm_summary or analysis["summary"]

        incident = Incident(
            title=payload.title,
            log=payload.log,
            category=analysis["category"],
            severity=analysis["severity"],
            summary=summary,
            probable_causes_json=json.dumps(
                analysis["probable_causes"],
                ensure_ascii=False,
            ),
            actions_json=json.dumps(
                analysis["recommended_actions"],
                ensure_ascii=False,
            ),
            sources_json=json.dumps(sources, ensure_ascii=False),
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        return AnalyzeIncidentResponse(
            incident_id=incident.id,
            category=analysis["category"],
            severity=analysis["severity"],
            summary=summary,
            probable_causes=analysis["probable_causes"],
            recommended_actions=analysis["recommended_actions"],
            matched_rules=analysis["matched_rules"],
            sources=sources,
            llm_used=llm_summary is not None,
        )
