"""HTTP client for the local FastAPI backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from shared.constants import API_BASE_URL, DEFAULT_TOLERANCE_CENTS

DEFAULT_BASE_URL = API_BASE_URL
DEFAULT_TIMEOUT_SECONDS = 600.0
HEALTH_CHECK_TIMEOUT_SECONDS = 5.0

BACKEND_UNAVAILABLE_CODE = "backend_unavailable"
BACKEND_UNAVAILABLE_MESSAGE = (
    "The local analysis server is not available. "
    "Start the backend on port 8765 and try again."
)


@dataclass(frozen=True)
class ApiError(Exception):
    """Structured API or connectivity failure."""

    error_code: str
    message: str
    details: dict[str, Any]

    def __str__(self) -> str:
        return self.message


class HcsaApiClient:
    """Synchronous httpx client for HCSA backend endpoints."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        return self._get_json("/health", timeout_seconds=HEALTH_CHECK_TIMEOUT_SECONDS)

    def inspect_audio(self, path: Path, *, role: str) -> dict[str, Any]:
        return self._post_multipart(
            "/audio/inspect",
            files={"file": (path.name, path.read_bytes())},
            data={"role": role},
        )

    def compare_audio(
        self,
        guru_path: Path | None = None,
        disciple_path: Path | None = None,
        *,
        tolerance_cents: int = DEFAULT_TOLERANCE_CENTS,
    ) -> dict[str, Any]:
        """
        Compare using session pitch cached from inspect.

        When both paths are omitted, the backend reuses inspect timelines (no re-upload).
        """
        if guru_path is None and disciple_path is None:
            return self._post_multipart(
                "/compare",
                files={},
                data={"tolerance_cents": str(tolerance_cents)},
            )
        if guru_path is None or disciple_path is None:
            raise ValueError("Provide both guru_path and disciple_path, or neither for session compare.")
        return self._post_multipart(
            "/compare",
            files={
                "guru_file": (guru_path.name, guru_path.read_bytes()),
                "disciple_file": (disciple_path.name, disciple_path.read_bytes()),
            },
            data={"tolerance_cents": str(tolerance_cents)},
        )

    def get_comparison_pitch(self) -> dict[str, Any]:
        """Fetch cached guru and disciple pitch timelines for graph rendering."""
        return self._get_json("/compare/pitch")

    def clear_session(self) -> dict[str, Any]:
        return self._post_json("/session/clear")

    def _get_json(self, path: str, *, timeout_seconds: float | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        timeout = timeout_seconds if timeout_seconds is not None else self.timeout_seconds
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
        except httpx.RequestError as exc:
            raise ApiError(
                BACKEND_UNAVAILABLE_CODE,
                BACKEND_UNAVAILABLE_MESSAGE,
                {"reason": str(exc)},
            ) from exc
        return self._parse_response(response)

    def _post_json(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url)
        except httpx.RequestError as exc:
            raise ApiError(
                BACKEND_UNAVAILABLE_CODE,
                BACKEND_UNAVAILABLE_MESSAGE,
                {"reason": str(exc)},
            ) from exc
        return self._parse_response(response)

    def _post_multipart(
        self,
        path: str,
        *,
        files: dict[str, tuple[str, bytes]],
        data: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        multipart_files = [
            (field_name, (file_name, content, "application/octet-stream"))
            for field_name, (file_name, content) in files.items()
        ]
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, files=multipart_files, data=data or {})
        except httpx.RequestError as exc:
            raise ApiError(
                BACKEND_UNAVAILABLE_CODE,
                BACKEND_UNAVAILABLE_MESSAGE,
                {"reason": str(exc)},
            ) from exc
        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            raise self._error_from_response(response)
        payload = response.json()
        if not isinstance(payload, dict):
            raise ApiError(
                "comparison_failed",
                "Unexpected response from the analysis server.",
                {},
            )
        return payload

    def _error_from_response(self, response: httpx.Response) -> ApiError:
        try:
            body = response.json()
        except Exception:
            return ApiError(
                BACKEND_UNAVAILABLE_CODE,
                BACKEND_UNAVAILABLE_MESSAGE,
                {"status_code": response.status_code},
            )
        if isinstance(body, dict) and "error_code" in body and "message" in body:
            details = body.get("details")
            if not isinstance(details, dict):
                details = {}
            return ApiError(
                str(body["error_code"]),
                str(body["message"]),
                details,
            )
        return ApiError(
            "comparison_failed",
            "The analysis server returned an error.",
            {"status_code": response.status_code, "body": body},
        )
