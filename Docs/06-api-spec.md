# API Spec

## Overview

The backend is a local FastAPI service used by the Python desktop frontend. The API must bind only to localhost in MVP.

Base URL:

```txt
http://127.0.0.1:8765/api/v1
```

MVP uses a static local port **8765**. The desktop app and backend subprocess must use this port consistently.

## Verbose logging

Optional console logging for route steps and pitch extraction timing:

- `HCSA_VERBOSE=1` in the environment, or
- `?verbose=true` on any request, or
- Header `X-HCSA-Verbose: 1`

When enabled, logs include request/response lines, per-step `start`/`done` with `elapsed_s`, pyin configuration, and **`pyin progress` lines with `percent`** (long audio is processed in `PYIN_CHUNK_SECONDS` slices). Structured API errors are logged at WARNING even when verbose is off.

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

Validate one uploaded audio file, run pitch extraction for vocal checks, and return file metadata plus a short pitch preview (not the full timeline).

Request:

- Content type: `multipart/form-data`
- Field: `file`
- Field: `role`, allowed values `guru`, `disciple`

Success response:

```json
{
  "file_info": {
    "file_id": "guru-001",
    "file_name": "guru.wav",
    "duration_seconds": 42.5,
    "sample_rate": 44100,
    "channels": 1,
    "format": "wav",
    "validation_status": "valid",
    "error_message": null
  },
  "pitch_metadata": {
    "voiced_frame_count": 1200,
    "total_frame_count": 1500,
    "voiced_fraction": 0.8,
    "preview_frames": [
      {
        "time_seconds": 0.0,
        "frequency_hz": 245.2,
        "confidence": 0.91,
        "voiced": true,
        "silent_or_unvoiced": false
      }
    ]
  }
}
```

Inspect behavior:

- `preview_frames` contains only the **first 5** frames (`INSPECT_PITCH_PREVIEW_FRAMES` in `config.py`).
- `voiced_frame_count`, `total_frame_count`, and `voiced_fraction` describe the **full** extracted timeline (used for validation).
- Full `PitchFrame` lists are returned only from `POST /compare`.
- Returns `no_vocals_detected` when pitch is too sparse (same thresholds as compare).

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

## Endpoint: Compare

```txt
POST /compare
```

Purpose:

Load guru and disciple recordings, extract pitch for each, and return graph-ready pitch frame arrays.

Request:

- Content type: `multipart/form-data`
- Field: `guru_file`
- Field: `disciple_file`

Example request fields:

```txt
guru_file=@guru.wav
disciple_file=@disciple.wav
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
  "guru_pitch_frames": [],
  "disciple_pitch_frames": [],
  "guru_summary": {
    "voiced_frame_count": 1200,
    "total_frame_count": 1500,
    "voiced_fraction": 0.8
  },
  "disciple_summary": {
    "voiced_frame_count": 1100,
    "total_frame_count": 1600,
    "voiced_fraction": 0.69
  },
  "warnings": []
}
```

Comparison behavior:

- Guru and disciple files may have different durations as long as each file is 5 minutes or shorter.
- Supported formats: WAV and MP3 only.
- Backend preserves full timeline; does not trim silence.
- Each `PitchFrame` uses `time_seconds` from the start of that recording (wall-clock).
- Frontend plots `frequency_hz` vs `time_seconds` for each series (omit or break line where `frequency_hz` is null).
- No Sa normalization, swara labels, DTW, matched segments, or scoring in MVP.

## Endpoint: Clear Session

```txt
POST /session/clear
```

Purpose:

Clear or refresh all temporary app data for the current local session.

Behavior:

- Clears uploaded/inspected file references.
- Clears cached analysis results.
- Resets processing state.
- Deletes all temporary session files on disk.

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
| `comparison_failed` | Unexpected comparison failure. |
| `backend_unavailable` | Frontend cannot reach the local backend (client-side). |

## Out of scope for MVP (API to be added later)

### Endpoints not in minimal spec

- `GET /settings/tolerance`
- `PUT /settings/tolerance`
- `GET /swara-map`

Existing implementations may retain these until code is updated; new work should follow this spec.

### Compare request/response fields not in minimal spec

- Request: `tolerance_cents`
- Response: `guru_sa_hz`, `disciple_sa_hz`, `tolerance_cents`, `matched_segments`, `excluded_guru_ranges`, `excluded_disciple_ranges`, `aligned_frames`, `metrics` (`ComparisonMetrics`)

### Error codes not in minimal spec

- `sa_detection_failed`
- `no_matching_pattern`
- `invalid_tolerance`

### Compare behavior not in minimal spec

- Normalize pitch relative to detected Sa per recording.
- Find similar portions; DTW inside matched segments only.
- Score and graph matched regions only; concatenated `aligned_time` for graph X-axis.
- Classify frames as match/higher/lower/unknown using tolerance.

## Frontend API Client Behavior

- Run basic client-side file validation before `POST /audio/inspect` (extension `.wav`/`.mp3`, file exists, size > 0, duration ≤ 300 s when metadata is available).
- Start backend process if needed on port **8765**.
- Poll `GET /health` until backend is ready.
- Use `POST /audio/inspect` after each file selection.
- Use `POST /compare` when user clicks Compare (guru + disciple files only).
- Use `POST /session/clear` when user clicks Clear; after an error popup is dismissed, reset the UI and delete all local temporary files.
- Display progress locally while request is running.
- Display structured error messages as modal popups.
- After any error popup is dismissed, refresh/reset the UI, delete temporary files, and require the user to start from the beginning.
