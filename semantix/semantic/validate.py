from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationIssue:
    code: str
    message: str
    path: str | None = None


def validate_mdl(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    models = doc.get("models")
    if not isinstance(models, list) or len(models) == 0:
        issues.append(ValidationIssue(code="empty_models", message="MDL must declare at least one model"))
        return issues

    model_names: set[str] = set()
    for i, model in enumerate(models):
        if not isinstance(model, dict):
            issues.append(ValidationIssue(code="invalid_model", message="Model must be an object", path=f"models[{i}]"))
            continue
        name = model.get("name")
        if not name:
            issues.append(ValidationIssue(code="missing_model_name", message="Model name is required", path=f"models[{i}]"))
        elif name in model_names:
            issues.append(ValidationIssue(code="duplicate_model", message=f"Duplicate model: {name}", path=f"models[{i}].name"))
        else:
            model_names.add(name)
        if not model.get("table"):
            issues.append(ValidationIssue(code="missing_table", message="Model table is required", path=f"models[{i}].table"))

    metrics = doc.get("metrics") or []
    if not isinstance(metrics, list):
        issues.append(ValidationIssue(code="invalid_metrics", message="metrics must be a list"))
        return issues
    for i, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            issues.append(ValidationIssue(code="invalid_metric", message="Metric must be an object", path=f"metrics[{i}]"))
            continue
        if not metric.get("name"):
            issues.append(ValidationIssue(code="missing_metric_name", message="Metric name required", path=f"metrics[{i}].name"))
        if not metric.get("expression"):
            issues.append(
                ValidationIssue(code="missing_expression", message="Metric expression required", path=f"metrics[{i}].expression")
            )
        model_name = metric.get("model")
        if model_name and model_name not in model_names:
            issues.append(
                ValidationIssue(
                    code="unknown_metric_model",
                    message=f"Metric references unknown model: {model_name}",
                    path=f"metrics[{i}].model",
                )
            )
    return issues
