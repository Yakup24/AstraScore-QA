from __future__ import annotations

from pathlib import Path
from typing import Any

from defusedxml.ElementTree import ParseError, fromstring


def render_template(template_path: str | Path, values: dict[str, Any]) -> str:
    """Render a tiny {{placeholder}} XML template without adding a template engine dependency."""
    text = Path(template_path).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def _strip_namespace(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def xml_text(xml_body: str, local_name: str) -> str | None:
    """Find text by local XML element name, ignoring namespaces."""
    root = fromstring(xml_body)
    for element in root.iter():
        if _strip_namespace(element.tag) == local_name:
            return element.text
    return None


def parse_score_response(xml_body: str) -> dict[str, Any]:
    """Parse an AstraScore QA SOAP scoring response into a Python dict."""
    score_text = xml_text(xml_body, "score")
    return {
        "transaction_id": xml_text(xml_body, "transactionId"),
        "status": xml_text(xml_body, "status"),
        "model_code": xml_text(xml_body, "modelCode"),
        "model_version": xml_text(xml_body, "modelVersion"),
        "score": int(score_text) if score_text is not None else None,
        "decision": xml_text(xml_body, "decision"),
    }


def is_soap_fault(xml_body: str) -> bool:
    try:
        root = fromstring(xml_body)
    except ParseError:
        return False
    return any(_strip_namespace(element.tag) == "Fault" for element in root.iter())
