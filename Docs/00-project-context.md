# Project Context

## Project Name

Hindustani Classical Music Learning App

## Purpose

This project is a local Windows desktop app for comparing a guru's vocal recording with a disciple's vocal recording. The app extracts fundamental frequency (F0) from each file with `librosa.pyin` and displays both pitch contours on one graph over wall-clock time.

## Spec Workflow

This repository follows a spec-driven workflow:

1. `00-project-context.md`: shared project context and build rules.
2. `01-prd.md`: locked product requirements.
3. `02-user-journeys.md`: user workflows and scenarios.
4. `03-functional-spec.md`: functional requirements.
5. `04-ux-spec.md`: UI layout, states, and graph behavior.
6. `05-data-model.md`: internal and API data structures.
7. `06-api-spec.md`: local FastAPI contract.
8. `07-architecture.md`: implementation architecture.
9. `08-test-plan.md`: verification strategy.
10. `09-implementation-plan.md`: build sequence.
11. `10-cursor-build-brief.md`: Cursor implementation brief.

Product defaults and pyin thresholds are summarized in `07-architecture.md` (port **8765**, vocal cutoffs).

## Locked MVP Decisions

- Platform: Windows desktop first.
- Runtime: Python `3.11.x`.
- UI: Python desktop frontend using `PySide6`.
- Graphing: `pyqtgraph`.
- Backend: local `FastAPI` API served through `uvicorn`.
- Audio analysis: `librosa` as the main DSP engine.
- Pitch extraction: `librosa.pyin`.
- Numeric processing: `numpy`, `scipy`.
- Audio file reading: `soundfile`, with packaged FFmpeg support through `imageio-ffmpeg`.
- Packaging: `PyInstaller`.
- Scope: upload two files, extract pitch, overlay both contours on one graph (Hz vs wall-clock time).

## Out of scope for MVP (to be added later)

The following were in the original Hindustani-comparison design and are **not** in the minimal MVP. Re-add only when explicitly requested.

### Pitch normalization and swaras

- Auto-detect Sa per recording (`guru_sa_hz`, `disciple_sa_hz`).
- Cents-relative pitch (`cents_from_sa`) for cross-key comparison.
- Indian swara mapping and symbols (`S r R g G m M P d D n N`, 100-cent bins).
- Swara Y-axis labels on the graph (komal/tivra).
- `GET /swara-map` and `Swara` data model.

### Alignment, matching, and scoring

- Matched-portion discovery (sliding windows, similarity thresholds).
- DTW alignment inside matched segments (`librosa.sequence.dtw`).
- Compare/score **matched portions only**; exclude non-similar extra material.
- Concatenated `aligned_time` X-axis (alignment index, not wall-clock).
- Per-frame difference in cents and tolerance-based classification (`match`, `higher`, `lower`, `unknown`).
- Tolerance UI (0–25 cents, step 5) and `GET`/`PUT /settings/tolerance`.
- `tolerance_cents` on compare request.
- Summary metrics: `overall_score`, average deviation, match/higher/lower/unknown percentages.
- `ComparisonFrame`, `ComparisonMetrics`, `MatchedSegment`, `ExcludedRange` in API responses.
- Errors: `sa_detection_failed`, `no_matching_pattern`, `invalid_tolerance`.
- Graph: tolerance band, match/higher/lower highlights, matched-only view.
- Highest deviation points metric.

### Other product features (unchanged non-goals)

- Live recording, real-time feedback, audio playback, export.
- Detailed rhythm, taal, laya, or early/late timing analysis.
- Coaching text or qualitative practice advice.
- M4A and other formats beyond WAV/MP3.

## Product Constraints

- The app must run offline.
- Audio files must remain local.
- The FastAPI server must bind only to localhost in MVP.
- The UI must be a single page.
- The full uploaded audio timeline must be preserved in pitch extraction (no trimming).
- The app must not trim leading silence, trailing silence, long endings, or non-vocal silent sections.
- Guru and disciple clips may have different durations as long as each file is 5 minutes or shorter.
- The graph plots **full-timeline** F0 for both recordings on **wall-clock** `time_seconds` (no concatenated alignment index).
- Comparison is in **Hz** on the Y-axis (linear scale; log scale is a later UX option).
- Errors must be shown as popups.
- After an error popup is dismissed, the UI must reset and the user must start again.

## Default Settings

- Maximum audio length: 5 minutes per file.
- Clip durations may differ.
- Supported upload formats: WAV and MP3 only (M4A out of scope for MVP).
- Backend base URL: `http://127.0.0.1:8765/api/v1` (static port).
- Initial analysis sample rate: 22050 Hz.
- Initial pitch range: 50 Hz to 1000 Hz.
- UI language: English.

## Development Principles

- Keep backend analysis separate from frontend rendering.
- Keep the API contract frontend-agnostic so React or Kotlin frontends can be added later.
- Prefer simple deterministic logic for MVP over heavy ML dependencies.
- Add focused tests around audio loading, pitch extraction, API responses, and graph rendering.
- Do not add later-scope features unless explicitly requested.
