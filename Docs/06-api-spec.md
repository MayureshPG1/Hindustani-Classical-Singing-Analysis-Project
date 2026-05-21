# API Spec

## Overview

The backend is a local FastAPI service used by the Python desktop frontend. The API must bind only to localhost in MVP.

Base URL:

```txt
http://127.0.0.1:8765/api/v1
```

MVP uses a static local port **8765**. The desktop app and backend subprocess must use this port consistently.

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
  "message": "Audio file must be 5 minutes or shorter.",
  "details": {
    "duration_seconds": 301.2,
    "max_duration_seconds": 300
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
  "tolerance_cents": 0,
  "default_tolerance_cents": 0,
  "step_cents": 5,
  "minimum_tolerance_cents": 0,
  "maximum_tolerance_cents": 25
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
  "tolerance_cents": 15
}
```

Response:

```json
{
  "tolerance_cents": 15,
  "default_tolerance_cents": 0,
  "step_cents": 5,
  "minimum_tolerance_cents": 0,
  "maximum_tolerance_cents": 25
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
tolerance_cents=0
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
  "tolerance_cents": 0,
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

- Guru and disciple files may have different durations as long as each file is 5 minutes or shorter.
- Supported formats: WAV and MP3 only.
- Backend must find similar pitch-contour portions and compare those portions (see [`07-architecture.md`](07-architecture.md) for algorithm parameters).
- DTW runs only inside each `MatchedSegment`, not on full-file contours.
- Non-similar additional portions from either file are left out of comparison and scoring.
- Graph-ready `aligned_frames` and pitch arrays in the response cover **matched portions only**; `aligned_time` is a cumulative index across concatenated matched segments (0…N−1).
- `overall_score` = `total_matching_intervals * 100 / total_intervals` over comparable frames in matched regions.
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
- Deletes all temporary session files on disk.
- Restores tolerance to default 0 unless frontend explicitly sets another value afterward.

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
| `file_too_long` | File duration exceeds 300 seconds (5 minutes). |
| `no_audio_detected` | Decoded file contains no usable audio data. |
| `decode_failed` | Backend could not decode audio. |
| `no_vocals_detected` | Audio exists, but no usable vocal pitch pattern was found (includes cases where pitch extraction is too sparse). |
| `sa_detection_failed` | Sa could not be estimated reliably. |
| `no_matching_pattern` | Guru and disciple recordings do not contain a sufficiently similar pitch-contour portion to compare. |
| `comparison_failed` | Unexpected comparison failure. |
| `invalid_tolerance` | Tolerance is missing, non-numeric, or outside allowed bounds. |

## Frontend API Client Behavior

- Run basic client-side file validation before `POST /audio/inspect` (extension `.wav`/`.mp3`, file exists, size > 0, duration ≤ 300 s when metadata is available).
- Start backend process if needed on port **8765**.
- Poll `GET /health` until backend is ready.
- Use `GET /settings/tolerance` on startup to initialize tolerance UI.
- Use `PUT /settings/tolerance` when tolerance changes or before compare.
- Use `POST /audio/inspect` after each file selection.
- Use `POST /compare` when user clicks Compare.
- Use `POST /session/clear` when user clicks Clear; after an error popup is dismissed, reset the UI and delete all local temporary files (calling clear is optional if the client already wipes session state and temp dirs).
- Display progress locally while request is running.
- Display structured error messages as modal popups.
- After any error popup is dismissed, refresh/reset the UI, delete temporary files, and require the user to start from the beginning.
