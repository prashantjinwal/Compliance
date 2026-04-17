from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import yaml

from ingestion.models import RegulatoryEvent, RouteTarget


DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "routing_rules.yaml"


class RoutingEngine:
    def __init__(self, rules_path: Path | str = DEFAULT_RULES_PATH):
        data = yaml.safe_load(Path(rules_path).read_text(encoding="utf-8")) or {}
        self.rules = data.get("rules", [])
        self.defaults = data.get("defaults", {})

    def route(self, event: RegulatoryEvent) -> list[RouteTarget]:
        regulation = event.normalized
        targets: set[RouteTarget] = set()

        for rule in self.rules:
            if not self._matches(rule, event):
                continue
            targets.update(RouteTarget(target) for target in rule.get("targets", []))

        if event.event_type.value != "NO_CHANGE" and not targets:
            targets.update(RouteTarget(target) for target in self.defaults.get("material_targets", []))

        if self._is_near_effective_date(event):
            targets.add(RouteTarget.ALERTING_QUEUE)

        if not targets:
            targets.add(RouteTarget.STORE_ONLY)

        if RouteTarget.STORE_ONLY in targets and len(targets) > 1:
            targets.remove(RouteTarget.STORE_ONLY)

        return sorted(targets, key=lambda target: target.value)

    def _matches(self, rule: dict, event: RegulatoryEvent) -> bool:
        regulation = event.normalized
        if "domains" in rule and regulation.domain not in rule["domains"]:
            return False
        if "change_types" in rule and event.event_type.value not in rule["change_types"]:
            return False
        if "exclude_change_types" in rule and event.event_type.value in rule["exclude_change_types"]:
            return False
        if "urgency" in rule and regulation.urgency != rule["urgency"]:
            return False
        return True

    def _is_near_effective_date(self, event: RegulatoryEvent) -> bool:
        effective_date = event.normalized.effective_date
        if not effective_date:
            return False
        window = int(self.defaults.get("alert_window_days", 14))
        now = datetime.utcnow()
        return now <= effective_date.replace(tzinfo=None) <= now + timedelta(days=window)

