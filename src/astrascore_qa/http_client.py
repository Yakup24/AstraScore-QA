from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from time import sleep
from typing import Any

import requests

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class HttpClient:
    base_url: str
    timeout: tuple[int | float, int | float] = (3, 10)
    retries: int = 1
    retry_backoff_seconds: float = 0.2
    default_headers: Mapping[str, str] | None = None

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Send a request with lightweight retry support for transient failures."""
        headers = self._headers(kwargs.pop("headers", None))
        last_error: requests.RequestException | None = None

        for attempt in range(self.retries + 1):
            try:
                response = requests.request(
                    method,
                    self._url(path),
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self.retries:
                    raise
                self._sleep_before_retry(attempt)
                continue

            if response.status_code not in RETRYABLE_STATUS_CODES or attempt >= self.retries:
                return response
            self._sleep_before_retry(attempt)

        if last_error:
            raise last_error
        raise RuntimeError("HTTP request failed without a response")

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post_json(self, path: str, payload: dict[str, Any], **kwargs: Any) -> requests.Response:
        headers = {"Content-Type": "application/json", **kwargs.pop("headers", {})}
        return self.request("POST", path, json=payload, headers=headers, **kwargs)

    def post_xml(self, path: str, xml_body: str, soap_action: str | None = None, **kwargs: Any) -> requests.Response:
        headers = {"Content-Type": "text/xml; charset=utf-8", **kwargs.pop("headers", {})}
        if soap_action:
            headers["SOAPAction"] = soap_action
        return self.request("POST", path, data=xml_body.encode("utf-8"), headers=headers, **kwargs)

    def _headers(self, headers: Mapping[str, str] | None = None) -> dict[str, str]:
        return {**dict(self.default_headers or {}), **dict(headers or {})}

    def _sleep_before_retry(self, attempt: int) -> None:
        if self.retry_backoff_seconds > 0:
            sleep(self.retry_backoff_seconds * (attempt + 1))
