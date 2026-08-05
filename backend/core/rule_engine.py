import re


class RuleEngine:
    def __init__(self):
        self.rules = []

    def add_rule(self, name: str, pattern: str = None,
                 condition: str = None, message: str = "",
                 severity: str = "medium"):
        self.rules.append({
            "name": name,
            "pattern": pattern,
            "condition": condition,
            "message": message,
            "severity": severity,
        })

    def evaluate(self, text: str) -> list:
        results = []
        for rule in self.rules:
            passed = True
            if rule["pattern"]:
                passed = bool(re.search(rule["pattern"], text, re.IGNORECASE))
            results.append({
                "rule": rule["name"],
                "passed": passed,
                "message": rule["message"],
                "severity": rule["severity"],
            })
        return results


DEFAULT_DOCUMENT_RULES = [
    {
        "name": "Has Executive Summary",
        "pattern": r"executive\s+summary",
        "message": "Document should contain an executive summary",
        "severity": "high",
    },
    {
        "name": "Has Objectives",
        "pattern": r"(objectives?|goals?)",
        "message": "Document should clearly state objectives",
        "severity": "high",
    },
    {
        "name": "Has Timeline",
        "pattern": r"(timeline|schedule|milestone|deadline)",
        "message": "Document should include a timeline",
        "severity": "medium",
    },
    {
        "name": "Has Risk Assessment",
        "pattern": r"(risk|mitigation|hazard)",
        "message": "Document should include risk assessment",
        "severity": "medium",
    },
    {
        "name": "Has Success Metrics",
        "pattern": r"(success\s+metric|kpi|measure|metric)",
        "message": "Document should define success metrics",
        "severity": "medium",
    },
    {
        "name": "Has Stakeholders",
        "pattern": r"(stakeholder|audience|participant)",
        "message": "Document should identify stakeholders",
        "severity": "low",
    },
    {
        "name": "Has Budget/Cost",
        "pattern": r"(budget|cost|expense|financial|roi)",
        "message": "Document should address budget/cost considerations",
        "severity": "medium",
    },
    {
        "name": "Min Length",
        "condition": "length >= 500",
        "message": "Document should be at least 500 characters",
        "severity": "high",
    },
]


def get_default_rule_engine() -> RuleEngine:
    engine = RuleEngine()
    for rule in DEFAULT_DOCUMENT_RULES:
        engine.add_rule(**rule)
    return engine


def validate_document(text: str, custom_rules: list = None) -> dict:
    engine = get_default_rule_engine()
    if custom_rules:
        for rule in custom_rules:
            engine.add_rule(**rule)
    results = engine.evaluate(text)
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "total_rules": total,
        "passed": passed,
        "failed": total - passed,
        "compliance_score": round((passed / total * 100) if total > 0 else 0, 2),
        "results": results,
    }
