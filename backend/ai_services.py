"""
Bridge module for LangChain AI services.

These function signatures match what the rest of the Django backend expects.
"""

import logging
from datetime import date, timedelta

from copilot.rag.config import CopilotConfigurationError
from copilot.rag.errors import CopilotRateLimitError


logger = logging.getLogger(__name__)


def analyze_regulation(raw_text: str) -> dict:
    """
    Analyze regulation text using LangChain.

    Expected return:
        {
            "summary": str,
            "key_changes": str,
            "obligations": list[str],
            "relevance_score": float
        }
    """
    try:
        from copilot.rag.pipeline import analyze_regulation as _ai_analyze

        return _ai_analyze(raw_text)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("analyze_regulation: AI service unavailable - using placeholder")
        return {
            "summary": "AI analysis pending. Service not yet connected.",
            "key_changes": "",
            "obligations": [],
            "relevance_score": 0.0,
        }
    except (CopilotConfigurationError, CopilotRateLimitError):
        raise
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
    """
    try:
        from copilot.rag.pipeline import assess_risk as _ai_assess

        return _ai_assess(analysis_data)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("assess_risk: AI service unavailable - using placeholder")
        return {
            "risk_level": "medium",
            "impacted_area": "General Compliance",
            "description": "Risk assessment pending. Review manually.",
        }
    except (CopilotConfigurationError, CopilotRateLimitError):
        raise
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
    """
    try:
        from copilot.rag.pipeline import generate_tasks as _ai_tasks

        return _ai_tasks(risk_data)
    except (ImportError, AttributeError, NotImplementedError):
        logger.warning("generate_tasks: AI service unavailable - using placeholder")
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
    except (CopilotConfigurationError, CopilotRateLimitError):
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_tasks raised an unexpected error: %s", exc)
        return []
