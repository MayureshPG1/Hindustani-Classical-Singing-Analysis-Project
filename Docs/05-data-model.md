# Data Model

## Overview

The app has three main data areas:

- File metadata.
- Audio analysis frames.
- Comparison result data.

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
detecting_sa
finding_matching_portions
aligning
calculating_comparison
generating_graph
complete
error
```

### FrameClassification

```txt
match
higher
lower
unknown
```

### ExclusionReason

```txt
no_matching_counterpart
silence_or_unvoiced
low_confidence
outside_matched_region
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

Example:

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

## ToleranceSettings

Represents comparison tolerance.

Fields:

- `tolerance_cents`: float.
- `default_tolerance_cents`: float, default 0.
- `step_cents`: float, default 5.
- `minimum_tolerance_cents`: float, default 0.
- `maximum_tolerance_cents`: float, default 25.

Example:

```json
{
  "tolerance_cents": 0,
  "default_tolerance_cents": 0,
  "step_cents": 5,
  "minimum_tolerance_cents": 0,
  "maximum_tolerance_cents": 25
}
```

## Swara

Represents a swara label and compact symbol.

Fields:

- `label`: string.
- `symbol`: string.
- `cents_from_sa`: float.

Note:

- A swara does not have one fixed F0 globally.
- The actual swara F0 depends on the detected Sa for the recording.
- Per-frame debug fields store the calculated Sa F0 and mapped swara F0.

MVP symbols:

```json
[
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
```

## PitchFrame

Represents pitch analysis for one time frame from one recording.

Fields:

- `time_seconds`: float.
- `frequency_hz`: optional float.
- `confidence`: optional float.
- `voiced`: boolean.
- `silent_or_unvoiced`: boolean.
- `cents_from_sa`: optional float.
- `sa_f0_hz`: optional float, detected Sa F0 used for this frame.
- `swara_label`: optional string.
- `swara_symbol`: optional string.
- `swara_f0_hz`: optional float, expected F0 of the mapped swara based on detected Sa.

Example voiced frame:

```json
{
  "time_seconds": 1.25,
  "frequency_hz": 245.2,
  "confidence": 0.91,
  "voiced": true,
  "silent_or_unvoiced": false,
  "cents_from_sa": 702.1,
  "sa_f0_hz": 164.8,
  "swara_label": "Pa",
  "swara_symbol": "P",
  "swara_f0_hz": 247.2
}
```

Example unvoiced frame:

```json
{
  "time_seconds": 1.5,
  "frequency_hz": null,
  "confidence": 0.12,
  "voiced": false,
  "silent_or_unvoiced": true,
  "cents_from_sa": null,
  "sa_f0_hz": 164.8,
  "swara_label": null,
  "swara_symbol": null,
  "swara_f0_hz": null
}
```

## TimeRange

Represents a range in one source recording.

Fields:

- `start_seconds`: float.
- `end_seconds`: float.

## ExcludedRange

Represents a portion of a source recording that was left out of comparison.

Fields:

- `source`: string, allowed values `guru` or `disciple`.
- `start_seconds`: float.
- `end_seconds`: float.
- `reason`: `ExclusionReason`.

## MatchedSegment

Represents a similar portion found between guru and disciple recordings.

Fields:

- `segment_id`: string.
- `guru_range`: `TimeRange`.
- `disciple_range`: `TimeRange`.
- `similarity_score`: optional float.

## ComparisonFrame

Represents one aligned comparison point.

Fields:

- `aligned_time`: float.
- `original_guru_time`: optional float.
- `original_disciple_time`: optional float.
- `guru_cents_from_sa`: optional float.
- `disciple_cents_from_sa`: optional float.
- `guru_sa_f0_hz`: optional float.
- `disciple_sa_f0_hz`: optional float.
- `guru_swara_label`: optional string.
- `guru_swara_symbol`: optional string.
- `guru_swara_f0_hz`: optional float.
- `disciple_swara_label`: optional string.
- `disciple_swara_symbol`: optional string.
- `disciple_swara_f0_hz`: optional float.
- `difference_cents`: optional float.
- `classification`: `FrameClassification`.

Example:

```json
{
  "aligned_time": 3.2,
  "original_guru_time": 3.1,
  "original_disciple_time": 3.4,
  "guru_cents_from_sa": 386.0,
  "disciple_cents_from_sa": 430.0,
  "guru_sa_f0_hz": 164.8,
  "disciple_sa_f0_hz": 146.8,
  "guru_swara_label": "Shuddha Ga",
  "guru_swara_symbol": "G",
  "guru_swara_f0_hz": 207.6,
  "disciple_swara_label": "Shuddha Ga",
  "disciple_swara_symbol": "G",
  "disciple_swara_f0_hz": 185.0,
  "difference_cents": 44.0,
  "classification": "match"
}
```

## ComparisonMetrics

Fields:

- `overall_score`: float. Formula: `total_matching_intervals * 100 / total_intervals`, where the numerator counts frames classified as `match` and the denominator counts all comparable frames in matched regions.
- `total_matching_intervals`: integer (optional explicit field for clients/tests).
- `total_intervals`: integer (optional explicit field for clients/tests).
- `average_deviation_cents`: float.
- `match_percentage`: float.
- `higher_percentage`: float.
- `lower_percentage`: float.
- `unknown_percentage`: float.
- `comparable_frame_count`: integer.
- `matched_frame_count`: integer.
- `excluded_frame_count`: integer.
- `total_frame_count`: integer.

## ComparisonResult

Top-level API response for comparison.

Fields:

- `guru_file_info`: `AudioFileInfo`.
- `disciple_file_info`: `AudioFileInfo`.
- `guru_sa_hz`: optional float, detected Sa F0 for guru.
- `disciple_sa_hz`: optional float, detected Sa F0 for disciple.
- `tolerance_cents`: float.
- `guru_pitch_frames`: list of `PitchFrame`.
- `disciple_pitch_frames`: list of `PitchFrame`.
- `matched_segments`: list of `MatchedSegment`.
- `excluded_guru_ranges`: list of `ExcludedRange`.
- `excluded_disciple_ranges`: list of `ExcludedRange`.
- `aligned_frames`: list of `ComparisonFrame`.
- `metrics`: `ComparisonMetrics`.
- `warnings`: list of string.

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
- `sa_detection_failed`
- `no_matching_pattern`
- `comparison_failed`
- `backend_unavailable`
