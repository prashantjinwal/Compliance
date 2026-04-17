"""
ai_services.py — Bridge module for LangChain AI services.

These function signatures match what the AI team has implemented.
All three are called by regulations/services.py during the compliance pipeline.

Integration point: replace the try/except bodies with actual imports once
the AI team exposes their functions.
"""

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


def analyze_regulation(raw_text: str) -> dict:
    """
    Analyze regulation text using LangChain.

    Expected return:
        {
            "summary": str,
            "key_changes": str,
            "obligations": list[str],
            "relevance_score": float  # 0.0 – 1.0
        }
    """
    try:
        # ── Swap this import for the actual LangChain entry-point ──────────
        from copilot.rag.pipeline import analyze_regulation as _ai_analyze  # noqa
        return _ai_analyze(raw_text)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("analyze_regulation: AI service unavailable — using placeholder")
        return {
            "summary": "AI analysis pending. Service not yet connected.",
            "key_changes": "",
            "obligations": [],
            "relevance_score": 0.0,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("analyze_regulation raised an unexpected error: %s", exc)
        return {
            "summary": f"Analysis failed: {exc}",
            "key_changes": "",
            "obligations": [],
            "relevance_score": 0.0,
        }


def assess_risk(analysis_data: dict) -> dict:
    """
    Assess compliance risk based on analysis output.

    Args:
        analysis_data: dict with keys summary, key_changes, obligations

    Expected return:
        {
            "risk_level": "low" | "medium" | "high" | "critical",
            "impacted_area": str,
            "description": str
        }
    """
    try:
        from copilot.rag.pipeline import assess_risk as _ai_assess  # noqa
        return _ai_assess(analysis_data)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("assess_risk: AI service unavailable — using placeholder")
        return {
            "risk_level": "medium",
            "impacted_area": "General Compliance",
            "description": "Risk assessment pending. Review manually.",
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("assess_risk raised an unexpected error: %s", exc)
        return {
            "risk_level": "medium",
            "impacted_area": "Unknown",
            "description": f"Assessment failed: {exc}",
        }


def generate_tasks(risk_data: dict) -> list:
    """
    Generate compliance tasks from risk assessment output.

    Args:
        risk_data: dict with keys risk_level, impacted_area, description, regulation_title

    Expected return:
        [
            {
                "title": str,
                "description": str,
                "suggested_action": str,
                "deadline": str | date,   # ISO-8601 string or date object
                "assigned_role": str      # e.g. "Legal", "IT", "Finance"
            },
            ...
        ]
    """
    try:
        from copilot.rag.pipeline import generate_tasks as _ai_tasks  # noqa
        return _ai_tasks(risk_data)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("generate_tasks: AI service unavailable — using placeholder")
        return [
            {
                "title": f"Review: {risk_data.get('regulation_title', 'Regulation')}",
                "description": (
                    f"Auto-generated task for {risk_data.get('impacted_area', 'compliance area')}. "
                    "Customize before assigning."
                ),
                "suggested_action": "Review the regulation and assign to the appropriate team member.",
                "deadline": (date.today() + timedelta(days=7)).isoformat(),
                "assigned_role": "Legal",
            }
        ]
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_tasks raised an unexpected error: %s", exc)
        return []
