from pathlib import Path

from semantix.semantic.mdl import parse_mdl_yaml
from semantix.semantic.validate import validate_mdl


def test_rejects_empty_models():
    issues = validate_mdl({"models": []})
    assert any(i.code == "empty_models" for i in issues)


def test_example_mdl_valid():
    text = Path("mdl/examples/device_online_rate.yml").read_text(encoding="utf-8")
    doc, issues = parse_mdl_yaml(text)
    assert issues == []
    assert doc["metrics"][0]["name"] == "device_online_rate"
