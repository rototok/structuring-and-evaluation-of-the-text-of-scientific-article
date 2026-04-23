"""
IMRAD structure analysis module.

Called from tasks.py for the "structure" analysis module.
Runs the full analysis pipeline:
  1. classify_sections  — locate I / M / R / D in the raw text
  2. analyze_*          — analyse each section independently
  3. summarize          — produce the final IMRAD compliance report
"""

import json
import logging

from services.llm_service import (
    classify_sections,
    analyze_introduction,
    analyze_methods,
    analyze_results,
    analyze_discussion,
    summarize,
)

logger = logging.getLogger(__name__)


def _parse_classification(raw: str) -> dict[str, str]:
    """
    Extract the JSON block returned by classify_sections.
    Falls back to using the full article text for every section if parsing fails.
    """
    try:
        # The model may wrap the JSON in ```json … ``` fences — strip them.
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Could not parse section classification JSON; falling back to full text.")
        return {}


def run(article_text: str) -> str:
    """
    Run the full IMRAD structure analysis and return a markdown report.
    """
    logger.info("Starting IMRAD structure analysis …")

    # Step 1 — classify sections
    raw_classification = classify_sections(article_text)
    sections = _parse_classification(raw_classification)
    logger.info("Section classification done.")

    # Step 2 — analyse each section.
    # If classification failed or a section is marked absent we still pass
    # the full article text so the model can do its best.
    def _section(key: str) -> str:
        value = sections.get(key, "")
        if not value or value.strip().lower() == "отсутствует":
            return article_text
        return value

    intro_result = analyze_introduction(_section("introduction"))
    logger.info("Introduction analysis done.")

    methods_result = analyze_methods(_section("methods"))
    logger.info("Methods analysis done.")

    results_result = analyze_results(_section("introduction"), _section("results"))
    logger.info("Results analysis done.")

    discussion_result = analyze_discussion(_section("introduction"), _section("discussion"))
    logger.info("Discussion analysis done.")

    # Step 3 — final summary
    final_report = summarize(
        intro_analysis=intro_result,
        methods_analysis=methods_result,
        results_analysis=results_result,
        discussion_analysis=discussion_result,
    )
    logger.info("Summary done.")

    # Assemble the full structured report
    report = "\n\n---\n\n".join([
        "# Анализ структуры IMRAD\n\n## Классификация разделов\n" + raw_classification,
        "## Introduction\n" + intro_result,
        "## Methods\n" + methods_result,
        "## Results\n" + results_result,
        "## Discussion\n" + discussion_result,
        "## Итоговая оценка\n" + final_report,
    ])

    return report