from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from astrascore_qa.http_client import HttpClient


@pytest.mark.smoke
def test_http_client_retries_transient_500(monkeypatch):
    first_response = requests.Response()
    first_response.status_code = 500
    first_response._content = b'{"status":"temporary_error"}'
    second_response = requests.Response()
    second_response.status_code = 200
    second_response._content = b'{"status":"ok"}'
    request_mock = Mock(side_effect=[first_response, second_response])
    monkeypatch.setattr(requests, "request", request_mock)

    client = HttpClient(base_url="http://example.test", retries=1, retry_backoff_seconds=0)
    response = client.get("/health")

    assert response.status_code == 200
    assert request_mock.call_count == 2


@pytest.mark.smoke
def test_http_client_raises_after_timeout_retry(monkeypatch):
    request_mock = Mock(side_effect=requests.Timeout("synthetic timeout"))
    monkeypatch.setattr(requests, "request", request_mock)

    client = HttpClient(base_url="http://example.test", retries=1, retry_backoff_seconds=0)

    with pytest.raises(requests.Timeout, match="synthetic timeout"):
        client.get("/health")
    assert request_mock.call_count == 2
