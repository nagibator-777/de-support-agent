import json

import typer

from app.database import Base, SessionLocal, engine
from app.schemas import AnalyzeIncidentRequest
from app.services.incident_service import IncidentService

cli = typer.Typer(help="CLI для анализа инцидентов Data Engineering.")


@cli.command()
def analyze(
    log_file: str = typer.Argument(..., help="Путь к файлу с логом"),
    title: str = typer.Option("CLI incident", "--title", "-t"),
    no_llm: bool = typer.Option(False, "--no-llm"),
) -> None:
    """Проанализировать лог и вывести структурированный результат."""
    with open(log_file, "r", encoding="utf-8") as file:
        log = file.read()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        result = IncidentService(db).analyze_and_save(
            AnalyzeIncidentRequest(
                title=title,
                log=log,
                use_llm=not no_llm,
            )
        )

    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
