"""API client response parsing and error mapping tests."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from frontend.api_client import (
    BACKEND_UNAVAILABLE_CODE,
    ApiError,
    HcsaApiClient,
)


def test_parse_success_response() -> None:
    client = HcsaApiClient()
    response = httpx.Response(200, json={"status": "ok", "version": "0.1.0"})
    assert client._parse_response(response)["status"] == "ok"


def test_parse_structured_error_response() -> None:
    client = HcsaApiClient()
    response = httpx.Response(
        400,
        json={
            "error_code": "file_too_long",
            "message": "Audio file must be 5 minutes or shorter.",
            "details": {"duration_seconds": 301.0},
        },
    )
    with pytest.raises(ApiError) as exc_info:
        client._parse_response(response)
    assert exc_info.value.error_code == "file_too_long"
    assert exc_info.value.details["duration_seconds"] == 301.0


def test_health_uses_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path.endswith("/health")
        return httpx.Response(200, json={"status": "ok", "version": "0.1.0"})

    transport = httpx.MockTransport(handler)
    api = HcsaApiClient(base_url="http://127.0.0.1:8765/api/v1")

    def _get_json(path: str, *, timeout_seconds: float | None = None) -> dict:
        with httpx.Client(transport=transport, base_url=api.base_url) as http:
            return api._parse_response(http.get(path))

    api._get_json = _get_json
    assert api.health()["status"] == "ok"


def test_inspect_raises_api_error(tmp_path: Path) -> None:
    wav = tmp_path / "guru.wav"
    wav.write_bytes(b"RIFF")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error_code": "no_vocals_detected",
                "message": "No reliable vocal pitch was detected.",
                "details": {},
            },
        )

    transport = httpx.MockTransport(handler)
    api = HcsaApiClient(base_url="http://127.0.0.1:8765/api/v1")

    def _post_multipart(
        path: str,
        *,
        files: dict[str, tuple[str, bytes]],
        data: dict[str, str] | None = None,
    ) -> dict:
        multipart_files = [
            (field_name, (file_name, content, "application/octet-stream"))
            for field_name, (file_name, content) in files.items()
        ]
        with httpx.Client(transport=transport, base_url=api.base_url) as http:
            return api._parse_response(http.post(path, files=multipart_files, data=data or {}))

    api._post_multipart = _post_multipart
    with pytest.raises(ApiError) as exc_info:
        api.inspect_audio(wav, role="guru")
    assert exc_info.value.error_code == "no_vocals_detected"


def test_request_error_maps_to_backend_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    class _BrokenClient:
        def __enter__(self):
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def get(self, _url: str) -> httpx.Response:
            raise httpx.ConnectError("refused", request=httpx.Request("GET", "http://test"))

    monkeypatch.setattr(httpx, "Client", lambda **_kwargs: _BrokenClient())
    api = HcsaApiClient(base_url="http://127.0.0.1:8765/api/v1", timeout_seconds=0.01)
    with pytest.raises(ApiError) as exc_info:
        api.health()
    assert exc_info.value.error_code == BACKEND_UNAVAILABLE_CODE
