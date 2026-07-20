from app.services.analyzer import analyze_log


def test_postgres_connection_error():
    result = analyze_log(
        "psycopg.OperationalError: connection refused while connecting to server"
    )

    assert result["category"] == "postgresql"
    assert result["severity"] == "high"
    assert "postgres_connection_refused" in result["matched_rules"]


def test_unknown_error():
    result = analyze_log("Something unusual happened")

    assert result["category"] == "unknown"
    assert result["severity"] == "low"
