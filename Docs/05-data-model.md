# Data Model

## Overview

The app has three main data areas:

- File metadata.
- Pitch frames per recording.
- Comparison result (summary metrics from wall-clock Hz scoring).

These models should be implemented as Pydantic models in the backend where they cross the API boundary.

## Enums

### ValidationStatus

```txt
empty
loading
valid
invalid
```

### ProcessingStatus

```txt
idle
loading_audio
extracting_pitch
generating_graph
complete
error
```

## AudioFileInfo

Represents file metadata after upload or validation.

Fields:

- `file_id`: string, generated per API request/session.
- `file_name`: string.
- `duration_seconds`: float.
- `sample_rate`: integer.
- `channels`: integer.
- `format`: string.
- `validation_status`: `ValidationStatus`.
- `error_message`: optional string.

## PitchMetadata

Pitch summary for `POST /audio/inspect` (full-timeline stats only; no per-frame arrays).

Fields:

- `voiced_frame_count`: integer (full timeline).
- `total_frame_count`: integer (full timeline).
- `voiced_fraction`: float (full timeline).

## AudioInspectResponse

Response for `POST /audio/inspect`.

Fields:

- `file_info`: `AudioFileInfo`.
- `pitch_metadata`: `PitchMetadata`.

Example:

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
    "voiced_fraction": 0.8
  }
}
```

## PitchFrame (`models/pitch.py`)

Represents pitch analysis for one time frame from one recording.

Fields:

- `time_seconds`: float.
- `frequency_hz`: optional float (null when unvoiced or unreliable).
- `confidence`: optional float (voiced probability from pyin).
- `voiced`: boolean.
- `silent_or_unvoiced`: boolean.

Example voiced frame:

```json
{
  "time_seconds": 1.25,
  "frequency_hz": 245.2,
  "confidence": 0.91,
  "voiced": true,
  "silent_or_unvoiced": false
}
```

Example unvoiced frame:

```json
{
  "time_seconds": 1.5,
  "frequency_hz": null,
  "confidence": 0.12,
  "voiced": false,
  "silent_or_unvoiced": true
}
```

## PitchSummary (`models/pitch.py`)

Lightweight per-file stats. Used in inspect `pitch_metadata` counts (not returned from compare).

Fields:

- `voiced_frame_count`: integer.
- `total_frame_count`: integer.
- `voiced_fraction`: float.

## ComparisonSummary

Wall-clock Hz comparison metrics (v1: no Sa, no DTW).

Fields:

- `overall_score`: float (0–100; same as `match_percentage`).
- `average_deviation_cents`: float (mean absolute Hz-ratio deviation in cents).
- `match_percentage`: float.
- `higher_percentage`: float (disciple sharper than guru beyond tolerance).
- `lower_percentage`: float.
- `tolerance_cents`: int (0–25; tolerance used for classification).

## ComparisonResult

Top-level API response for `POST /compare`.

Fields:

- `guru_file_info`: `AudioFileInfo`.
- `disciple_file_info`: `AudioFileInfo`.
- `comparison_summary`: `ComparisonSummary`.

Example:

```json
{
  "guru_file_info": { "file_name": "guru.wav", "duration_seconds": 42.5 },
  "disciple_file_info": { "file_name": "disciple.wav", "duration_seconds": 44.1 },
  "comparison_summary": {
    "overall_score": 72.5,
    "average_deviation_cents": 18.3,
    "match_percentage": 72.5,
    "higher_percentage": 15.0,
    "lower_percentage": 12.5,
    "tolerance_cents": 10
  }
}
```

Full `PitchFrame` lists are **not** returned from compare (inspect uses `pitch_metadata` only). A separate pitch endpoint may be added later for graph UI.

## ErrorResponse

Fields:

- `error_code`: string.
- `message`: string.
- `details`: optional object.

Common error codes:

- `unsupported_file_type`
- `file_too_long`
- `no_audio_detected`
- `decode_failed`
- `no_vocals_detected`
- `comparison_failed` (no overlapping voiced pairs to score)
- `invalid_tolerance` (tolerance not in 0–25)
- `backend_unavailable`

## Out of scope for MVP (models to be added later)

The following types and fields are **not** in the minimal MVP spec:

| Item | Purpose when added |
| --- | --- |
| `ToleranceSettings` | Tolerance get/set API (0–25 cents) |
| `Swara` | Swara table for labels and `GET /swara-map` |
| `TimeRange`, `MatchedSegment` | Guru/disciple ranges for matched portions |
| `ExcludedRange`, `ExclusionReason` | Portions left out of compare/score |
| `ComparisonFrame` | Aligned compare point (`aligned_time`, cents, classification) |
| `FrameClassification` | `match`, `higher`, `lower`, `unknown` |
| `guru_sa_hz`, `disciple_sa_hz` | Detected tonic per file (Sa + DTW phase) |
| `ComparisonMetrics` as separate type | Replaced by `ComparisonSummary` in compare response |
| `aligned_frames`, `matched_segments`, `excluded_*_ranges` | Alignment and scoring payload |
| `cents_from_sa`, `swara_*`, `sa_f0_hz` on `PitchFrame` | Sa-relative and swara debug fields |
| `ProcessingStatus` values | `detecting_sa`, `finding_matching_portions`, `aligning`, `calculating_comparison` |
