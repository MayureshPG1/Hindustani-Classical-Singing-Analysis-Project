# API Spec

## Overview

The backend is a local FastAPI service used by the Python desktop frontend. The API must bind only to localhost in MVP.

Base URL:

```txt
http://127.0.0.1:{port}/api/v1
```

The desktop app may choose an available local port at startup.

## API Principles

- Local-only.
- No authentication for MVP because the server is bound to localhost.
- Use Pydantic models for request and response schemas.
- Use multipart file upload for audio files.
- Return structured errors.
- Keep API frontend-agnostic for future React or Kotlin clients.

## Endpoint: Health Check

```txt
GET /health
```

Response:

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Endpoint: Inspect Audio

```txt
POST /audio/inspect
```

Purpose:

Validate one uploaded audio file and return metadata.

Request:

- Content type: `multipart/form-data`
- Field: `file`
- Field: `role`, allowed values `guru`, `disciple`

Success response:

```json
{
  "file_id": "guru-001",
  "file_name": "guru.wav",
  "duration_seconds": 42.5,
  "sample_rate": 44100,
  "channels": 1,
  "format": "wav",
  "validation_status": "valid",
  "error_message": null
}
```

Error response:

```json
{
  "error_code": "file_too_long",
  "message": "Audio file must be 2 minutes or shorter.",
  "details": {
    "duration_seconds": 151.2,
    "max_duration_seconds": 120
  }
}
```

## Endpoint: Get Tolerance

```txt
GET /settings/tolerance
```

Purpose:

Return the current tolerance setting used by the app.

Response:

```json
{
  "tolerance_cents": 50,
  "default_tolerance_cents": 50,
  "step_cents": 10,
  "minimum_tolerance_cents": null,
  "maximum_tolerance_cents": null
}
```

## Endpoint: Set Tolerance

```txt
PUT /settings/tolerance
```

Purpose:

Set the tolerance value to be used for subsequent comparisons.

Request:

```json
{
  "tolerance_cents": 60
}
```

Response:

```json
{
  "tolerance_cents": 60,
  "default_tolerance_cents": 50,
  "step_cents": 10,
  "minimum_tolerance_cents": null,
  "maximum_tolerance_cents": null
}
```

Error response:

```json
{
  "error_code": "invalid_tolerance",
  "message": "Tolerance must be numeric and within the allowed range.",
  "details": {
    "tolerance_cents": "abc"
  }
}
```

## Endpoint: Compare

```txt
POST /compare
```

Purpose:

Compare guru and disciple recordings and return graph-ready data plus metrics.

Request:

- Content type: `multipart/form-data`
- Field: `guru_file`
- Field: `disciple_file`
- Field: `tolerance_cents`

Example request fields:

```txt
guru_file=@guru.wav
disciple_file=@disciple.wav
tolerance_cents=50
```

Success response shape:

```json
{
  "guru_file_info": {
    "file_id": "guru-001",
    "file_name": "guru.wav",
    "duration_seconds": 42.5,
    "sample_rate": 44100,
    "channels": 1,
    "format": "wav",
    "validation_status": "valid",
    "error_message": null
  },
  "disciple_file_info": {
    "file_id": "disciple-001",
    "file_name": "disciple.wav",
    "duration_seconds": 44.1,
    "sample_rate": 44100,
    "channels": 1,
    "format": "wav",
    "validation_status": "valid",
    "error_message": null
  },
  "guru_sa_hz": 240.0,
  "disciple_sa_hz": 220.0,
  "tolerance_cents": 50,
  "guru_pitch_frames": [],
  "disciple_pitch_frames": [],
  "matched_segments": [],
  "excluded_guru_ranges": [],
  "excluded_disciple_ranges": [],
  "aligned_frames": [],
  "metrics": {
    "overall_score": 82.4,
    "average_deviation_cents": 31.5,
    "match_percentage": 76.0,
    "higher_percentage": 14.0,
    "lower_percentage": 7.0,
    "unknown_percentage": 3.0,
    "matched_frame_count": 760,
    "excluded_frame_count": 40,
    "comparable_frame_count": 760,
    "total_frame_count": 800
  },
  "warnings": []
}
```

Comparison behavior:

- Guru and disciple files may have different durations as long as each file is 2 minutes or shorter.
- Backend must find similar pitch-contour portions and compare those portions.
- Non-similar additional portions from either file are left out of comparison and scoring.
- Excluded portions are represented in `excluded_guru_ranges` and `excluded_disciple_ranges`.
- If no sufficiently similar vocal pattern is found, the API returns `no_matching_pattern`.

## Endpoint: Swara Mapping

```txt
GET /swara-map
```

Purpose:

Return the swara mapping used by backend and frontend.

Response:

```json
{
  "items": [
    {"label": "Sa", "symbol": "S", "cents_from_sa": 0},
    {"label": "Komal Re", "symbol": "r", "cents_from_sa": 100},
    {"label": "Shuddha Re", "symbol": "R", "cents_from_sa": 200},
    {"label": "Komal Ga", "symbol": "g", "cents_from_sa": 300},
    {"label": "Shuddha Ga", "symbol": "G", "cents_from_sa": 400},
    {"label": "Shuddha Ma", "symbol": "m", "cents_from_sa": 500},
    {"label": "Tivra Ma", "symbol": "M", "cents_from_sa": 600},
    {"label": "Pa", "symbol": "P", "cents_from_sa": 700},
    {"label": "Komal Dha", "symbol": "d", "cents_from_sa": 800},
    {"label": "Shuddha Dha", "symbol": "D", "cents_from_sa": 900},
    {"label": "Komal Ni", "symbol": "n", "cents_from_sa": 1000},
    {"label": "Shuddha Ni", "symbol": "N", "cents_from_sa": 1100}
  ]
}
```

## Endpoint: Clear Session

```txt
POST /session/clear
```

Purpose:

Clear or refresh all temporary app data for the current local session.

Behavior:

- Clears uploaded/inspected file references.
- Clears cached analysis results.
- Clears graph-ready comparison data.
- Resets processing state.
- Restores tolerance to default 50 unless frontend explicitly sets another value afterward.

Response:

```json
{
  "status": "cleared"
}
```

## Error Codes

| Code | Meaning |
| --- | --- |
| `unsupported_file_type` | File extension or decoded format is unsupported. |
| `file_too_long` | File duration exceeds 120 seconds. |
| `no_audio_detected` | Decoded file contains no usable audio data. |
| `decode_failed` | Backend could not decode audio. |
| `no_pitch_detected` | Pitch extraction found no reliable pitch. |
| `no_vocals_detected` | Audio exists, but no usable vocal pitch pattern was found. |
| `sa_detection_failed` | Sa could not be estimated reliably. |
| `no_matching_pattern` | Guru and disciple recordings do not contain a sufficiently similar pitch-contour portion to compare. |
| `comparison_failed` | Unexpected comparison failure. |
| `invalid_tolerance` | Tolerance is missing, non-numeric, or outside allowed bounds. |

## Frontend API Client Behavior

- Start backend process if needed.
- Poll `GET /health` until backend is ready.
- Use `GET /settings/tolerance` on startup to initialize tolerance UI.
- Use `PUT /settings/tolerance` when tolerance changes or before compare.
- Use `POST /audio/inspect` after each file selection.
- Use `POST /compare` when user clicks Compare.
- Use `POST /session/clear` when user clicks Clear or after an error popup is dismissed.
- Display progress locally while request is running.
- Display structured error messages as modal popups.
- After any error popup is dismissed, refresh/reset the UI and require the user to start from the beginning.
