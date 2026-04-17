"""
regulations/services.py

The compliance pipeline orchestrator.
Triggered automatically after a Regulation record is saved.

Sequence:
    1. analyze_regulation(raw_text)  → create Analysis
    2. assess_risk(analysis_data)    → create Risk
    3. generate_tasks(risk_data)     → create ComplianceTasks
    4. log every step via audit.utils.log_action
"""

import logging
from datetime import date, datetime

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract plain text from an uploaded PDF file.
    Replace with your actual PDF extraction library (PyMuPDF, pdfminer, etc.).
    """
    try:
        import fitz  # PyMuPDF
        pdf_file.seek(0)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass

    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        import io
        pdf_file.seek(0)
        output = io.StringIO()
        extract_text_to_fp(pdf_file, output, laparams=LAParams())
        return output.getvalue()
    except ImportError:
        pass

    logger.warning("No PDF extraction library available — returning empty text.")
    return ""


def run_compliance_pipeline(regulation, user):
    """
    Full pipeline: Analyze → Assess Risk → Generate Tasks → Audit Log.
    Must be called after the Regulation object is fully saved.
    Designed to run in a background thread.
    """
    from analysis.models import Analysis
    from risk.models import Risk
    from tasks.models import ComplianceTask
    from audit.utils import log_action
    from ai_services import (
        analyze_regulation,
        assess_risk,
        generate_tasks,
    )

    try:
        regulation.pipeline_status = "processing"
        regulation.save(update_fields=["pipeline_status"])

        # ── Step 1: AI Analysis ──────────────────────────────────────────────
        logger.info("Pipeline [%s]: Starting analysis", regulation.id)
        analysis_result = analyze_regulation(regulation.raw_text)

        analysis = Analysis.objects.create(
            regulation=regulation,
            organization=regulation.organization,
            summary=analysis_result.get("summary", ""),
            key_changes=analysis_result.get("key_changes", ""),
            obligations=analysis_result.get("obligations", []),
            relevance_score=float(analysis_result.get("relevance_score", 0.0)),
        )

        log_action(
            user=user,
            action="analysis_generated",
            entity_type="Analysis",
            entity_id=str(analysis.id),
            description=f"AI analysis generated for: {regulation.title}",
            organization=regulation.organization,
            metadata={"regulation_id": str(regulation.id)},
        )

        # ── Step 2: Risk Assessment ──────────────────────────────────────────
        logger.info("Pipeline [%s]: Assessing risk", regulation.id)
        risk_result = assess_risk({
            "summary": analysis.summary,
            "key_changes": analysis.key_changes,
            "obligations": analysis.obligations,
        })

        risk = Risk.objects.create(
            regulation=regulation,
            analysis=analysis,
            organization=regulation.organization,
            risk_level=risk_result.get("risk_level", "medium"),
            impacted_area=risk_result.get("impacted_area", "General Compliance"),
            description=risk_result.get("description", ""),
        )

        log_action(
            user=user,
            action="risk_assessed",
            entity_type="Risk",
            entity_id=str(risk.id),
            description=(
                f"Risk assessed for: {regulation.title} — "
                f"Level: {risk.get_risk_level_display()}"
            ),
            organization=regulation.organization,
            metadata={
                "regulation_id": str(regulation.id),
                "risk_level": risk.risk_level,
            },
        )

        # ── Step 3: Task Generation ──────────────────────────────────────────
        logger.info("Pipeline [%s]: Generating tasks", regulation.id)
        tasks_data = generate_tasks({
            "risk_level": risk.risk_level,
            "impacted_area": risk.impacted_area,
            "description": risk.description,
            "regulation_title": regulation.title,
        })

        for task_data in tasks_data or []:
            deadline = _parse_deadline(task_data.get("deadline"))

            task = ComplianceTask.objects.create(
                regulation=regulation,
                risk=risk,
                organization=regulation.organization,
                title=task_data.get("title", "Untitled Task"),
                description=task_data.get("description", ""),
                suggested_action=task_data.get("suggested_action", ""),
                deadline=deadline,
                assigned_role=task_data.get("assigned_role", "Legal"),
            )

            log_action(
                user=user,
                action="task_created",
                entity_type="ComplianceTask",
                entity_id=str(task.id),
                description=f"Task auto-created: {task.title}",
                organization=regulation.organization,
                metadata={
                    "regulation_id": str(regulation.id),
                    "risk_id": str(risk.id),
                    "assigned_role": task.assigned_role,
                },
            )

        # ── Done ─────────────────────────────────────────────────────────────
        regulation.pipeline_status = "completed"
        regulation.save(update_fields=["pipeline_status"])
        logger.info("Pipeline [%s]: Completed successfully", regulation.id)

    except Exception as exc:
        logger.exception("Pipeline failed for regulation %s: %s", regulation.id, exc)
        regulation.pipeline_status = "failed"
        regulation.save(update_fields=["pipeline_status"])
        raise


def _parse_deadline(raw) -> date | None:
    """Safely parse a deadline value from the AI response."""
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
    return None
