# DE Support Agent

Учебный backend-сервис для классификации технических логов и поиска рекомендаций для первой линии поддержки Data Engineering.

Приложение принимает текст ошибки, ищет известные сигнатуры, определяет категорию и критичность инцидента, подбирает инструкцию из локальной базы знаний и сохраняет результат в базе данных.

Основная диагностика работает без нейросети. В проекте также предусмотрен экспериментальный модуль GigaChat, который может использоваться для формирования более понятного итогового ответа.

## Зачем я сделал этот проект

Цель проекта — разобраться, как объединить в одном приложении:

- Python и FastAPI;
- обработку технических логов;
- REST API и валидацию данных;
- SQLAlchemy и базу данных;
- автоматические тесты;
- CLI-интерфейс;
- Docker Compose;
- опциональное подключение языковой модели.

Проект ориентирован на типовую задачу внутренней поддержки: пользователь отправляет лог, а сервис возвращает структурированную первичную диагностику.

## Что умеет сервис

- принимать технические логи через REST API;
- классифицировать известные ошибки;
- определять критичность инцидента;
- формировать список возможных причин;
- предлагать первичные действия для диагностики;
- искать подходящие инструкции в JSON-базе знаний;
- сохранять результаты анализа в SQLite или PostgreSQL;
- получать сохранённый инцидент по его идентификатору;
- выполнять базовую проверку SQL-запросов на read-only операции;
- анализировать файлы с логами через CLI;
- запускаться локально или через Docker Compose;
- выполнять unit- и API-тесты.

## Поддерживаемые сценарии

В текущей версии добавлены правила для следующих ошибок:

- PostgreSQL `connection refused`;
- отсутствующая таблица или relation;
- PostgreSQL deadlock;
- нарушение уникального ограничения;
- Hadoop/HDFS Safe Mode;
- нехватка места на диске;
- Python `ModuleNotFoundError`;
- Python `KeyError`;
- timeout зависимого сервиса.

## Важное ограничение

Основной анализ является rule-based.

Приложение использует регулярные выражения и заранее заданные правила:

```text
сигнатура ошибки
    ↓
категория
    ↓
критичность
    ↓
возможная причина
    ↓
рекомендуемое действие
```

Поэтому сервис хорошо работает с предусмотренными сценариями, но может вернуть:

```json
{
  "category": "unknown",
  "severity": "low"
}
```

если не найдёт подходящего правила.

Текущая версия не является полноценным AI-агентом и не выполняет самостоятельную диагностику инфраструктуры.

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
    +--> GigaChat Enhancer (опционально)
    |
    v
SQLAlchemy
    |
    v
SQLite / PostgreSQL
```

Основные компоненты проекта:

```text
app/main.py
```

REST API и маршруты FastAPI.

```text
app/services/analyzer.py
```

Правила классификации технических ошибок.

```text
app/services/knowledge.py
```

Поиск инструкций в локальной базе знаний.

```text
app/services/incident_service.py
```

Общий сценарий анализа и сохранения инцидента.

```text
app/services/sql_safety.py
```

Базовая проверка SQL-запросов.

```text
app/services/llm.py
```

Экспериментальный модуль интеграции с GigaChat.

```text
data/knowledge_base.json
```

Локальная база инструкций.

## Быстрый запуск на Windows

Требуется Python 3.11 или новее.

Проверка версии:

```powershell
py --version
```

Создание виртуального окружения:

```powershell
py -m venv .venv
```

Активация в PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скрипта:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Установка зависимостей:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Запуск сервера:

```powershell
python -m uvicorn app.main:app --reload
```

После запуска:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- API: `http://127.0.0.1:8000`

По умолчанию используется локальная SQLite-база:

```text
de_support.db
```

Поэтому PostgreSQL для первого запуска не требуется.

## Запуск на Linux или macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

## Проверка работы API

### Health check

Откройте в Swagger:

```text
GET /health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

### Анализ технического лога

Endpoint:

```text
POST /api/v1/incidents/analyze
```

Пример запроса:

```json
{
  "title": "Python-приложение не запускается",
  "log": "ModuleNotFoundError: No module named 'pandas'",
  "context": "Ошибка появилась после создания нового виртуального окружения",
  "use_llm": false
}
```

Пример ответа:

```json
{
  "incident_id": 1,
  "category": "python",
  "severity": "medium",
  "summary": "Обнаружено правил: 1. Основная категория: python; максимальная критичность: medium.",
  "probable_causes": [
    "Зависимость отсутствует в активном Python-окружении."
  ],
  "recommended_actions": [
    "Проверить виртуальное окружение, requirements и способ запуска приложения."
  ],
  "matched_rules": [
    "python_module_not_found"
  ],
  "sources": [
    "Python: проблемы окружения и зависимостей"
  ],
  "llm_used": false
}
```

### Получение сохранённого инцидента

Endpoint:

```text
GET /api/v1/incidents/{incident_id}
```

Например:

```text
GET /api/v1/incidents/1
```

## Проверка SQL-запросов

Endpoint:

```text
POST /api/v1/tools/sql-check
```

Безопасный запрос:

```json
{
  "query": "SELECT id, name FROM users WHERE id = 1"
}
```

Ответ:

```json
{
  "allowed": true,
  "reason": "Запрос выглядит read-only.",
  "normalized_query": "SELECT id, name FROM users WHERE id = 1"
}
```

Запрос на изменение данных:

```json
{
  "query": "DROP TABLE users"
}
```

будет заблокирован.

### Ограничение SQL-проверки

Текущая реализация выполняет только базовый текстовый анализ.

Она:

- разрешает запросы, начинающиеся с `SELECT` или `WITH`;
- блокирует очевидные операции изменения данных;
- запрещает несколько SQL-команд в одном запросе.

Это не является полноценной системой безопасности.

В production-среде дополнительно потребовались бы:

- пользователь базы данных с правами только на чтение;
- полноценный SQL-парсер;
- ограничения времени выполнения;
- лимиты количества возвращаемых строк;
- аудит выполняемых запросов.

## CLI

Для анализа файла с логом без Swagger:

```powershell
python -m app.cli analyze examples/postgres_connection.log `
  --title "Ошибка подключения" `
  --no-llm
```

Для Linux или macOS:

```bash
python -m app.cli analyze examples/postgres_connection.log \
  --title "Ошибка подключения" \
  --no-llm
```

## Docker Compose

В проекте подготовлена конфигурация для запуска API вместе с PostgreSQL.

Создайте `.env`.

Windows:

```powershell
Copy-Item .env.example .env
```

Linux или macOS:

```bash
cp .env.example .env
```

Запуск:

```bash
docker compose up --build
```

После запуска API будет доступен по адресу:

```text
http://127.0.0.1:8000/docs
```

## Экспериментальная интеграция с GigaChat

Основная диагностика не зависит от GigaChat и работает без API-ключа.

Модуль LLM используется только для преобразования найденной диагностики в более подробный текстовый ответ. Категорию и критичность инцидента определяет rule-based анализатор.

Для настройки необходимо создать файл `.env` и указать:

```env
GIGACHAT_CREDENTIALS=ваш_ключ
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat
```

После этого в запросе можно установить:

```json
{
  "use_llm": true
}
```

Файл `.env` включён в `.gitignore`. API-ключи нельзя добавлять в репозиторий.

Основной проверенный сценарий проекта работает с параметром:

```json
{
  "use_llm": false
}
```

## Тесты

Запуск всех тестов:

```bash
python -m pytest
```

Тесты проверяют:

- health endpoint;
- классификацию известных ошибок;
- обработку неизвестного лога;
- read-only SQL-проверку;
- блокировку опасных SQL-команд;
- работу endpoint анализа инцидента.

## Проверка кода

```bash
ruff check .
```

## Что я изучил во время разработки

Во время работы над проектом я разобрался:

- как FastAPI принимает и валидирует JSON-запросы;
- как работает Swagger и OpenAPI;
- как разделять API, бизнес-логику и слой хранения данных;
- как сохранять объекты через SQLAlchemy;
- как использовать SQLite для локального запуска;
- как писать unit- и API-тесты;
- как создавать CLI-интерфейс;
- как хранить настройки через переменные окружения;
- как приложение может продолжить работу при недоступности внешнего сервиса.

## Что пока не реализовано

- семантический поиск через embeddings;
- векторная база данных;
- настоящий цикл AI-агента с tool calling;
- выполнение диагностических команд на сервере;
- авторизация и роли пользователей;
- полноценная production-защита SQL;
- веб-интерфейс для обычного пользователя;
- система обратной связи по качеству рекомендаций.

## Идеи для развития

- добавить embeddings и векторный поиск;
- реализовать tool calling для диагностических инструментов;
- добавить структурированное логирование;
- подключить метрики Prometheus;
- реализовать авторизацию;
- добавить интеграцию с Jira или Telegram;
- собирать пользовательскую оценку рекомендаций;
- расширить набор правил для PostgreSQL, Hadoop и Python.

## Стек

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- SQLite;
- PostgreSQL;
- pytest;
- Typer;
- Docker Compose;
- GitHub Actions;
- GigaChat SDK — экспериментальный модуль.

## Лицензия

Проект распространяется под лицензией MIT.
