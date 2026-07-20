# DE Support Agent

Учебный AI-помощник первой линии поддержки Data Engineering. Сервис принимает
технический лог, классифицирует инцидент, оценивает критичность, ищет инструкции
в локальной базе знаний и сохраняет результат в БД.

Проект сделан как портфолио под стажировку Python/AI/LLM-разработчика.

## Возможности

- FastAPI REST API и автоматически генерируемая Swagger-документация;
- анализ PostgreSQL, Hadoop/HDFS, Python, Linux и сетевых ошибок;
- поиск релевантных инструкций в JSON-базе знаний;
- опциональная генерация итогового ответа через GigaChat;
- хранение инцидентов в PostgreSQL или SQLite;
- read-only проверка SQL-запросов;
- CLI для анализа файлов с логами;
- Docker Compose;
- тесты и GitHub Actions CI.

## Архитектура

```text
Пользователь
    |
    v
FastAPI / CLI
    |
    +--> Rule-based Log Analyzer
    |
    +--> Knowledge Base Search
    |
    +--> GigaChat (опционально)
    |
    v
PostgreSQL / SQLite
```

## Быстрый запуск без Docker

Требуется Python 3.11+.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

После запуска:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

По умолчанию используется локальная SQLite-база, поэтому PostgreSQL для
первого запуска не нужен.

## Запуск через Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

На Windows можно скопировать `.env.example` в `.env` вручную.

## Пример запроса

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/incidents/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "PostgreSQL недоступен",
    "log": "psycopg.OperationalError: connection refused",
    "use_llm": false
  }'
```

Пример ответа:

```json
{
  "incident_id": 1,
  "category": "postgresql",
  "severity": "high",
  "summary": "Обнаружено правил: 1. Основная категория: postgresql; максимальная критичность: high.",
  "probable_causes": [
    "PostgreSQL недоступен по указанному адресу или порту."
  ],
  "recommended_actions": [
    "Проверить доступность хоста, порт, состояние сервиса и сетевые правила."
  ],
  "matched_rules": [
    "postgres_connection_refused"
  ],
  "sources": [
    "PostgreSQL: диагностика connection refused"
  ],
  "llm_used": false
}
```

## CLI

```bash
python -m app.cli analyze examples/postgres_connection.log \
  --title "Ошибка подключения" \
  --no-llm
```

## Интеграция с GigaChat

Основная диагностика не зависит от LLM и работает без API-ключа. Чтобы включить
генерацию расширенного ответа, скопируйте `.env.example` в `.env` и заполните:

```env
GIGACHAT_CREDENTIALS=ваш_ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat
```

Не добавляйте `.env` и ключи в Git. Файл уже включён в `.gitignore`.

## Тесты

```bash
python -m pytest
```

Проверка стиля:

```bash
ruff check .
```

## Что продемонстрировано в проекте

- прикладной Python и ООП;
- REST API, Pydantic и FastAPI;
- интеграция LLM по API;
- сценарий AI-помощника;
- PostgreSQL и SQLAlchemy;
- обработка ошибок и graceful degradation;
- безопасная работа с SQL;
- Docker, Linux CLI, GitHub Actions;
- unit- и API-тестирование.

## Идеи для развития

- embeddings и векторный поиск вместо token-overlap;
- tool calling для вызова диагностических инструментов;
- авторизация и роли пользователей;
- метрики Prometheus и структурированные логи;
- обратная связь пользователя о качестве рекомендаций;
- интеграция с Jira или Telegram.
