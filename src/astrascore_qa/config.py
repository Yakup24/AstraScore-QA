from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(ValueError):
    """Raised when the AstraScore QA config is missing required values."""


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML config, apply environment overrides and validate it."""
    path = Path(config_path) if config_path else PROJECT_ROOT / "config" / "config.yaml"
    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    base_url = os.getenv("SCORING_BASE_URL")
    if base_url:
        config.setdefault("service", {})["base_url"] = base_url

    db_path = os.getenv("SCORING_DB_PATH")
    if db_path:
        config.setdefault("database", {})["sqlite_path"] = db_path

    log_file = os.getenv("SCORING_LOG_FILE")
    if log_file:
        config.setdefault("logging", {})["log_file"] = log_file

    model_code = os.getenv("SCORING_MODEL_CODE")
    if model_code:
        config.setdefault("model", {})["default_model_code"] = model_code

    connect_timeout = os.getenv("SCORING_CONNECT_TIMEOUT")
    if connect_timeout:
        config.setdefault("timeouts", {})["connect_seconds"] = _as_positive_number(
            connect_timeout,
            "SCORING_CONNECT_TIMEOUT",
        )

    read_timeout = os.getenv("SCORING_READ_TIMEOUT")
    if read_timeout:
        config.setdefault("timeouts", {})["read_seconds"] = _as_positive_number(
            read_timeout,
            "SCORING_READ_TIMEOUT",
        )

    validate_config(config)

    return config


def project_path(relative_path: str | Path) -> Path:
    """Resolve path relative to project root."""
    return PROJECT_ROOT / relative_path


def validate_config(config: dict[str, Any]) -> None:
    """Validate the minimum contract expected by clients and tests."""
    _require_sections(config, ("service", "database", "logging", "timeouts", "model"))

    service = config["service"]
    for key in ("base_url", "health_path", "soap_realtime_path", "rest_batch_path"):
        _require_non_empty_string(service, key, f"service.{key}")

    database = config["database"]
    _require_non_empty_string(database, "type", "database.type")
    if database["type"] != "sqlite":
        raise ConfigError("database.type currently supports only 'sqlite' in the demo adapter")
    _require_non_empty_string(database, "sqlite_path", "database.sqlite_path")

    logging = config["logging"]
    _require_non_empty_string(logging, "log_file", "logging.log_file")

    timeouts = config["timeouts"]
    for key in ("connect_seconds", "read_seconds"):
        timeouts[key] = _as_positive_number(timeouts.get(key), f"timeouts.{key}")

    http = config.get("http", {})
    if http:
        retries = http.get("retries", 0)
        if not isinstance(retries, int) or retries < 0:
            raise ConfigError("http.retries must be a non-negative integer")
        http["retry_backoff_seconds"] = _as_non_negative_number(
            http.get("retry_backoff_seconds", 0),
            "http.retry_backoff_seconds",
        )

    observability = config.get("observability", {})
    if observability:
        _require_non_empty_string(observability, "correlation_header", "observability.correlation_header")
        _require_non_empty_string(observability, "metrics_path", "observability.metrics_path")

    model = config["model"]
    _require_non_empty_string(model, "default_model_code", "model.default_model_code")
    decisions = model.get("accepted_decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ConfigError("model.accepted_decisions must be a non-empty list")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, str) or not decision.strip():
            raise ConfigError(f"model.accepted_decisions[{index}] must be a non-empty string")


def _require_sections(config: dict[str, Any], section_names: Iterable[str]) -> None:
    for section_name in section_names:
        if not isinstance(config.get(section_name), dict):
            raise ConfigError(f"Missing or invalid config section: {section_name}")


def _require_non_empty_string(section: dict[str, Any], key: str, label: str) -> None:
    value = section.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{label} must be a non-empty string")


def _as_positive_number(value: Any, label: str) -> int | float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be a positive number") from exc
    if number <= 0:
        raise ConfigError(f"{label} must be a positive number")
    return int(number) if number.is_integer() else number


def _as_non_negative_number(value: Any, label: str) -> int | float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{label} must be a non-negative number") from exc
    if number < 0:
        raise ConfigError(f"{label} must be a non-negative number")
    return int(number) if number.is_integer() else number
