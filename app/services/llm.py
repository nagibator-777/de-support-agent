from typing import Any

from app.config import get_settings


class GigaChatEnhancer:
    """Опциональный слой LLM. Без ключа проект работает в rule-based режиме."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def available(self) -> bool:
        return bool(self.settings.gigachat_credentials)

    def enhance(self, title: str, log: str, analysis: dict, sources: list[dict]) -> str | None:
        if not self.available:
            return None

        try:
            from gigachat import GigaChat
        except ImportError:
            return None

        source_text = "\n".join(
            f"- {item['title']}: {item['content']}" for item in sources
        )
        prompt = f"""
Ты — помощник первой линии поддержки Data Engineering.
Сформируй краткое техническое резюме инцидента на русском языке.
Не придумывай факты. Используй только лог, rule-based анализ и базу знаний.
Формат: 3–5 предложений, затем нумерованный план действий.

Заголовок: {title}
Лог:
{log[:6000]}

Rule-based анализ:
{analysis}

База знаний:
{source_text or "релевантных документов не найдено"}
""".strip()

        kwargs: dict[str, Any] = {
            "credentials": self.settings.gigachat_credentials,
            "scope": self.settings.gigachat_scope,
            "model": self.settings.gigachat_model,
        }
        if self.settings.gigachat_ca_bundle_file:
            kwargs["ca_bundle_file"] = self.settings.gigachat_ca_bundle_file

        try:
            with GigaChat(**kwargs) as client:
                response = client.chat.create(prompt)
            return self._extract_text(response)
        except Exception:
            # Отказ LLM не должен ломать основную диагностику.
            return None

    @staticmethod
    def _extract_text(response: Any) -> str | None:
        # Новый контракт SDK.
        messages = getattr(response, "messages", None)
        if messages:
            content = getattr(messages[0], "content", None)
            if isinstance(content, list) and content:
                text = getattr(content[0], "text", None)
                if text:
                    return str(text)
            if isinstance(content, str):
                return content

        # Совместимость со старым контрактом.
        choices = getattr(response, "choices", None)
        if choices:
            message = getattr(choices[0], "message", None)
            text = getattr(message, "content", None)
            if text:
                return str(text)

        return None
