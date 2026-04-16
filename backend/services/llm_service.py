import os
import logging
from functools import lru_cache
from llama_cpp import Llama


logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv(
    "LLM_MODEL_PATH",
    "./models/yandex-gpt-lite-instruct/YandexGPT-5-Lite-8B-instruct-Q4_K_M.gguf"
)

# Context window. YandexGPT-5-Lite-8B supports up to 32k depending on
# the quantisation variant, but 8192 is a safe default that fits in RAM.
N_CTX = int(os.getenv("LLM_N_CTX", "8192"))

# Number of CPU threads. Tune via env var; default matches the value in
# the original yandex_model.py.
N_THREADS = int(os.getenv("LLM_N_THREADS", "8"))

# GPU layers to offload (0 = CPU-only).
N_GPU_LAYERS = int(os.getenv("LLM_N_GPU_LAYERS", "0"))


@lru_cache(maxsize=1)
def _load_model() -> Llama:
    """Load the model exactly once per process."""
    logger.info("Loading LLM from %s …", MODEL_PATH)
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False,
    )
    logger.info("LLM loaded successfully.")
    return llm


# ---------------------------------------------------------------------------
# System prompt (shared across all IMRAD calls)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "Ты — эксперт по академическому письму и научной коммуникации. "
    "Твоя задача — анализировать научные статьи на соответствие структуре IMRAD. "
    "Отвечай строго по заданному формату. "
    "Не добавляй вступлений и заключений вне указанного формата. "
    "Язык ответа: русский."
)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

PROMPTS: dict[str, str] = {
    "classify": """\
Ниже приведён текст научной статьи. Определи, какие фрагменты текста относятся \
к каждому из компонентов IMRAD:
- Introduction (Введение)
- Methods (Методы / Материалы и методы)
- Results (Результаты)
- Discussion (Обсуждение)
- Other (Abstract, Conclusion, References и прочее)

Если явных заголовков нет — определи по содержанию.

Отвечай строго в формате JSON без каких-либо пояснений:
{{
  "introduction": "<первые и последние слова блока или 'отсутствует'>",
  "methods": "<...>",
  "results": "<...>",
  "discussion": "<...>",
  "other": "<...>"
}}

ТЕКСТ СТАТЬИ:
{article_text}
""",

    "introduction": """\
Ты анализируешь раздел Introduction (Введение) научной статьи.

ТЕКСТ РАЗДЕЛА:
{section_text}

---
ФОРМАТ ОТВЕТА (строго соблюдай заголовки):

## Присутствующие элементы
- Постановка проблемы и актуальность: [присутствует / частично / отсутствует] — [обоснование]
- Краткий обзор ключевой литературы: [присутствует / частично / отсутствует] — [обоснование]
- Указание пробела в существующих исследованиях: [присутствует / частично / отсутствует] — [обоснование]
- Формулировка цели, задач и/или гипотез: [присутствует / частично / отсутствует] — [обоснование]

## Оценка полноты
[недостаточно / удовлетворительно / хорошо]
Обоснование: [2–3 предложения]

## Рекомендации
[нумерованный список конкретных улучшений или "Существенных замечаний нет"]
""",

    "methods": """\
Ты анализируешь раздел Methods (Материалы и методы) научной статьи.

ТЕКСТ РАЗДЕЛА:
{section_text}

---
ФОРМАТ ОТВЕТА:

## Присутствующие элементы
- Объект и/или выборка исследования: [присутствует / частично / отсутствует] — [обоснование]
- Материалы, оборудование, ПО: [присутствует / частично / отсутствует] — [обоснование]
- Дизайн исследования: [присутствует / частично / отсутствует] — [обоснование]
- Процедуры сбора данных: [присутствует / частично / отсутствует] — [обоснование]
- Методы обработки и статистического анализа: [присутствует / частично / отсутствует] — [обоснование]

## Воспроизводимость
[недостаточно / удовлетворительно / хорошо]
Обоснование: [2–3 предложения]

## Рекомендации
[нумерованный список конкретных улучшений]
""",

    "results": """\
Ты анализируешь раздел Results (Результаты) научной статьи.

ТЕКСТ РАЗДЕЛА:
{section_text}

---
ФОРМАТ ОТВЕТА:

## Присутствующие элементы
- Представление основных данных и находок: [присутствует / частично / отсутствует] — [обоснование]
- Таблицы, графики, рисунки и отсылки к ним: [присутствует / частично / отсутствует] — [обоснование]
- Логичная привязка результатов к цели/гипотезам: [присутствует / частично / отсутствует] — [обоснование]

## Смешение с Discussion
[да / нет / частично] — [конкретные примеры из текста или "не обнаружено"]

## Оценка полноты и ясности
[недостаточно / удовлетворительно / хорошо]
Обоснование: [2–3 предложения]

## Рекомендации
[нумерованный список: что уточнить, что вынести в таблицы, что перенести в Discussion]
""",

    "discussion": """\
Ты анализируешь раздел Discussion (Обсуждение) научной статьи.

ТЕКСТ РАЗДЕЛА:
{section_text}

---
ФОРМАТ ОТВЕТА:

## Присутствующие элементы
- Интерпретация результатов и ответы на гипотезы введения: [присутствует / частично / отсутствует] — [обоснование]
- Сравнение с другими исследованиями: [присутствует / частично / отсутствует] — [обоснование]
- Ограничения исследования: [присутствует / частично / отсутствует] — [обоснование]
- Теоретические и/или практические следствия: [присутствует / частично / отсутствует] — [обоснование]
- Направления дальнейших исследований: [присутствует / частично / отсутствует] — [обоснование]

## Смешение с Results
[да / нет] — [примеры или "не обнаружено"]

## Оценка полноты и качества
[недостаточно / удовлетворительно / хорошо]
Обоснование: [2–3 предложения]

## Рекомендации
[нумерованный список конкретных шагов по улучшению]
""",

    "summary": """\
Ты завершаешь анализ научной статьи на соответствие структуре IMRAD.
Ниже приведены результаты анализа четырёх разделов.

АНАЛИЗ INTRODUCTION:
{intro_analysis}

АНАЛИЗ METHODS:
{methods_analysis}

АНАЛИЗ RESULTS:
{results_analysis}

АНАЛИЗ DISCUSSION:
{discussion_analysis}

---
Сформируй итоговый отчёт строго в следующем формате:

## Общая оценка
[соответствует полностью / частично соответствует / требует значительной переработки]

## Сводка по разделам
| Раздел | Оценка | Главная проблема |
|--------|--------|-----------------|
| Introduction | ... | ... |
| Methods | ... | ... |
| Results | ... | ... |
| Discussion | ... | ... |

## Сильные стороны
[маркированный список, минимум 2 пункта]

## Приоритетные проблемы
1. [самая критичная]
2. ...
3. ...

## План доработки
1. [первоочередное действие]
2. ...

## Риски отклонения при публикации
[список или "существенных рисков не выявлено"]
""",
}

# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1500"))
_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.15"))
_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
_REPEAT_PENALTY = float(os.getenv("LLM_REPEAT_PENALTY", "1.1"))


def _build_messages(user_content: str) -> list[dict]:
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _infer(user_content: str) -> str:
    """Run a single chat-completion inference call."""
    llm = _load_model()
    messages = _build_messages(user_content)

    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=_MAX_TOKENS,
        temperature=_TEMPERATURE,
        top_p=_TOP_P,
        repeat_penalty=_REPEAT_PENALTY,
    )
    return response["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Public API — one function per analysis step
# ---------------------------------------------------------------------------

def _truncate(text: str, max_chars: int = 12_000) -> str:
    """Trim section text to avoid context overflow on long articles."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n\n[… текст сокращён …]\n\n" + text[-half:]


def classify_sections(article_text: str) -> str:
    prompt = PROMPTS["classify"].format(article_text=_truncate(article_text, 20_000))
    return _infer(prompt)


def analyze_introduction(section_text: str) -> str:
    prompt = PROMPTS["introduction"].format(section_text=_truncate(section_text))
    return _infer(prompt)


def analyze_methods(section_text: str) -> str:
    prompt = PROMPTS["methods"].format(section_text=_truncate(section_text))
    return _infer(prompt)


def analyze_results(section_text: str) -> str:
    prompt = PROMPTS["results"].format(section_text=_truncate(section_text))
    return _infer(prompt)


def analyze_discussion(section_text: str) -> str:
    prompt = PROMPTS["discussion"].format(section_text=_truncate(section_text))
    return _infer(prompt)


def summarize(
    intro_analysis: str,
    methods_analysis: str,
    results_analysis: str,
    discussion_analysis: str,
) -> str:
    prompt = PROMPTS["summary"].format(
        intro_analysis=intro_analysis,
        methods_analysis=methods_analysis,
        results_analysis=results_analysis,
        discussion_analysis=discussion_analysis,
    )
    return _infer(prompt)