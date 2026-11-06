from typing import Any

import yaml

from semantix.semantic.validate import ValidationIssue, validate_mdl


def parse_mdl_yaml(text: str) -> tuple[dict[str, Any], list[ValidationIssue]]:
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        return {}, [ValidationIssue(code="yaml_error", message=str(exc))]
    if not isinstance(doc, dict):
        return {}, [ValidationIssue(code="invalid_root", message="MDL root must be a mapping")]
    return doc, validate_mdl(doc)


def dump_mdl_yaml(doc: dict[str, Any]) -> str:
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)
