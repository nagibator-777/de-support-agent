from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    category: str
    severity: str
    cause: str
    action: str


RULES = [
    Rule(
        name="postgres_connection_refused",
        pattern=re.compile(r"connection refused|could not connect to server", re.I),
        category="postgresql",
        severity="high",
        cause="PostgreSQL недоступен по указанному адресу или порту.",
        action="Проверить доступность хоста, порт, состояние сервиса и сетевые правила.",
    ),
    Rule(
        name="postgres_missing_relation",
        pattern=re.compile(r"relation .* does not exist|table .* does not exist", re.I),
        category="postgresql",
        severity="medium",
        cause="Таблица отсутствует либо используется неверная схема.",
        action="Проверить search_path, имя схемы, миграции и регистр идентификатора.",
    ),
    Rule(
        name="postgres_deadlock",
        pattern=re.compile(r"deadlock detected", re.I),
        category="postgresql",
        severity="high",
        cause="Параллельные транзакции захватывают ресурсы в разном порядке.",
        action="Сократить транзакции, унифицировать порядок блокировок и добавить retry.",
    ),
    Rule(
        name="postgres_duplicate_key",
        pattern=re.compile(r"duplicate key value violates unique constraint", re.I),
        category="postgresql",
        severity="medium",
        cause="Запись конфликтует с уникальным ограничением.",
        action="Проверить генерацию ключа и выбрать корректную стратегию UPSERT.",
    ),
    Rule(
        name="hdfs_safe_mode",
        pattern=re.compile(r"safe mode|safemode", re.I),
        category="hadoop",
        severity="high",
        cause="NameNode находится в Safe Mode и блокирует операции записи.",
        action="Проверить состояние HDFS, количество живых DataNode и репликацию блоков.",
    ),
    Rule(
        name="disk_space",
        pattern=re.compile(r"no space left on device|disk quota exceeded", re.I),
        category="infrastructure",
        severity="critical",
        cause="На диске закончился объём либо превышена квота.",
        action="Проверить файловые системы, временные данные, логи и политику retention.",
    ),
    Rule(
        name="python_module_not_found",
        pattern=re.compile(r"ModuleNotFoundError|No module named", re.I),
        category="python",
        severity="medium",
        cause="Зависимость отсутствует в активном Python-окружении.",
        action="Проверить виртуальное окружение, requirements и способ запуска приложения.",
    ),
    Rule(
        name="python_key_error",
        pattern=re.compile(r"KeyError:", re.I),
        category="python",
        severity="medium",
        cause="Код обращается к отсутствующему ключу словаря или колонке данных.",
        action="Проверить входные данные и использовать явную валидацию перед обращением.",
    ),
    Rule(
        name="timeout",
        pattern=re.compile(r"timeout|timed out|deadline exceeded", re.I),
        category="network",
        severity="high",
        cause="Операция не завершилась в установленный таймаут.",
        action="Проверить зависимый сервис, сеть, объём данных и настройки retry/backoff.",
    ),
]

SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def analyze_log(log: str) -> dict:
    matched = [rule for rule in RULES if rule.pattern.search(log)]

    if not matched:
        return {
            "category": "unknown",
            "severity": "low",
            "summary": "Известные сигнатуры ошибок не найдены.",
            "probable_causes": [
                "Недостаточно контекста для уверенной автоматической классификации."
            ],
            "recommended_actions": [
                "Добавить полный traceback, время ошибки, имя сервиса и последние изменения."
            ],
            "matched_rules": [],
        }

    highest = max(matched, key=lambda rule: SEVERITY_ORDER[rule.severity])
    categories = [rule.category for rule in matched]
    primary_category = max(set(categories), key=categories.count)

    causes = list(dict.fromkeys(rule.cause for rule in matched))
    actions = list(dict.fromkeys(rule.action for rule in matched))

    return {
        "category": primary_category,
        "severity": highest.severity,
        "summary": (
            f"Обнаружено правил: {len(matched)}. "
            f"Основная категория: {primary_category}; "
            f"максимальная критичность: {highest.severity}."
        ),
        "probable_causes": causes,
        "recommended_actions": actions,
        "matched_rules": [rule.name for rule in matched],
    }
