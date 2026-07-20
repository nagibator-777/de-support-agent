import re


FORBIDDEN = re.compile(
    r"\b("
    r"insert|update|delete|drop|alter|truncate|create|grant|revoke|"
    r"copy|call|execute|merge|vacuum|analyze|refresh"
    r")\b",
    re.I,
)


def check_read_only_sql(query: str) -> dict:
    normalized = " ".join(query.strip().split())
    lowered = normalized.lower()

    if not normalized:
        return {
            "allowed": False,
            "reason": "Пустой запрос.",
            "normalized_query": normalized,
        }

    if ";" in normalized.rstrip(";"):
        return {
            "allowed": False,
            "reason": "Разрешён только один SQL-запрос.",
            "normalized_query": normalized,
        }

    if not (lowered.startswith("select ") or lowered.startswith("with ")):
        return {
            "allowed": False,
            "reason": "Разрешены только SELECT или WITH-запросы.",
            "normalized_query": normalized,
        }

    match = FORBIDDEN.search(normalized)
    if match:
        return {
            "allowed": False,
            "reason": f"Запрещённая SQL-операция: {match.group(1).upper()}.",
            "normalized_query": normalized,
        }

    return {
        "allowed": True,
        "reason": "Запрос выглядит read-only.",
        "normalized_query": normalized,
    }
