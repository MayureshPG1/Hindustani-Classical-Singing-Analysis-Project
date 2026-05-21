# Project Context

## Project Name

Hindustani Classical Music Learning App

## Purpose

This project is a local Windows desktop app for comparing a guru's vocal recording with a disciple's vocal recording. The app analyzes relative pitch contours, normalizes each recording to its detected Sa, and displays a single-page graphical comparison with statistical metrics.

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

Product defaults and analysis thresholds are also summarized in `07-architecture.md` (matched-portion discovery, pyin cutoffs, port 8765).

## Locked MVP Decisions

- Platform: Windows desktop first.
- Runtime: Python `3.11.x`.
- UI: Python desktop frontend using `PySide6`.
- Graphing: `pyqtgraph`.
- Backend: local `FastAPI` API served through `uvicorn`.
- Audio analysis: `librosa` as the main DSP engine.
- Pitch extraction: `librosa.pyin`.
- Alignment: `librosa.sequence.dtw`.
- Numeric processing: `numpy`, `scipy`.
- Audio file reading: `soundfile`, with packaged FFmpeg support through `imageio-ffmpeg`.
- Packaging: `PyInstaller`.
- Scope: upload two files, compare pitch contours, show graph and statistics.
- Out of scope: live recording, real-time feedback, audio playback, export, detailed rhythm/taal analysis, coaching text.

## Product Constraints

- The app must run offline.
- Audio files must remain local.
- The FastAPI server must bind only to localhost in MVP.
- The UI must be a single page.
- The full uploaded audio timeline must be preserved.
- The app must not trim leading silence, trailing silence, long endings, or non-vocal silent sections.
- Guru and disciple clips may have different durations as long as each file is 5 minutes or shorter.
- The backend must find similar portions between the two recordings and compare only those portions.
- Non-similar additional portions from either uploaded audio must be left out of comparison and scoring.
- Guru and disciple may sing in different scales.
- Comparison must be relative to each recording's detected Sa, not absolute pitch.
- The graph must show Indian swara labels including komal and tivra swaras.
- Errors must be shown as popups.
- After an error popup is dismissed, the UI must reset and the user must start again.

## Swara Mapping

| Swara Label | Symbol |
| --- | --- |
| Sa | S |
| Komal Re | r |
| Shuddha Re | R |
| Komal Ga | g |
| Shuddha Ga | G |
| Shuddha Ma | m |
| Tivra Ma | M |
| Pa | P |
| Komal Dha | d |
| Shuddha Dha | D |
| Komal Ni | n |
| Shuddha Ni | N |

## Default Settings

- Maximum audio length: 5 minutes per file.
- Clip durations may differ.
- Supported upload formats: WAV and MP3 only (M4A out of scope for MVP).
- Tolerance default: 0 cents.
- Tolerance range: 0 to 25 cents.
- Tolerance step size: 5 cents.
- Backend base URL: `http://127.0.0.1:8765/api/v1` (static port).
- Initial analysis sample rate: 22050 Hz.
- Initial pitch range: 50 Hz to 1000 Hz.
- UI language: English.
- Graph displays matched portions only; X-axis is concatenated alignment index across matched segments.
- Overall match score: `total_matching_intervals * 100 / total_intervals` in matched comparable frames.

## Development Principles

- Keep backend analysis separate from frontend rendering.
- Keep the API contract frontend-agnostic so React or Kotlin frontends can be added later.
- Prefer simple deterministic logic for MVP over heavy ML dependencies.
- Use custom app logic for Sa detection, swara mapping, tolerance classification, and scoring.
- Add focused tests around audio analysis, API responses, and graph data generation.
- Do not add later-scope features unless explicitly requested.
