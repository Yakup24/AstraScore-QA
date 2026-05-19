from __future__ import annotations

import pytest

from astrascore_qa.config import ConfigError, load_config, validate_config


def test_project_config_has_required_enterprise_contract(project_root):
    config = load_config(project_root / "config" / "config.yaml")

    assert config["service"]["base_url"].startswith("http")
    assert config["database"]["type"] == "sqlite"
    assert config["timeouts"]["connect_seconds"] > 0
    assert config["timeouts"]["read_seconds"] > 0
    assert config["http"]["retries"] >= 0
    assert config["observability"]["correlation_header"] == "X-Correlation-ID"
    assert "APPROVE" in config["model"]["accepted_decisions"]


def test_config_loader_applies_timeout_environment_overrides(project_root, monkeypatch):
    monkeypatch.setenv("SCORING_CONNECT_TIMEOUT", "1.5")
    monkeypatch.setenv("SCORING_READ_TIMEOUT", "7")

    config = load_config(project_root / "config" / "config.yaml")

    assert config["timeouts"]["connect_seconds"] == 1.5
    assert config["timeouts"]["read_seconds"] == 7


def test_config_validation_rejects_missing_required_sections():
    with pytest.raises(ConfigError, match="service"):
        validate_config({})

