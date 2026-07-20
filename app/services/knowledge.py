import json
import re
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zа-я0-9_]{3,}", re.I)


class KnowledgeBase:
    def __init__(self, path: Path):
        self.path = path
        self.documents = self._load()

    def _load(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("Knowledge base must contain a JSON list")
        return data

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token.lower() for token in TOKEN_RE.findall(text)}

    def search(self, query: str, limit: int = 3) -> list[dict]:
        query_tokens = self._tokens(query)
        scored: list[tuple[float, dict]] = []

        for document in self.documents:
            haystack = " ".join(
                [
                    document.get("title", ""),
                    " ".join(document.get("tags", [])),
                    document.get("content", ""),
                ]
            )
            doc_tokens = self._tokens(haystack)
            if not query_tokens or not doc_tokens:
                score = 0.0
            else:
                score = len(query_tokens & doc_tokens) / len(query_tokens | doc_tokens)
            scored.append((score, document))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for score, doc in scored[:limit] if score > 0]
