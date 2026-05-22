# Implementation Plan

## Build Strategy

Build the product in vertical slices. Start with backend pitch extraction correctness, then compare API, then frontend graph display, then packaging.

## Phase 0: Project Setup

Tasks:

- Create Python `3.11.x` virtual environment.
- Add `requirements.txt`.
- Create repository structure.
- Add basic lint-free Python package layout.
- Add minimal `pytest` setup.

Deliverables:

- Dependencies install successfully.
- Empty app modules import successfully.

## Phase 1: Backend Foundation

Tasks:

- Create FastAPI app.
- Add `/api/v1/health`.
- Add clear-session endpoint.
- Add Pydantic models (slim comparison models).
- Add structured error model.
- Add test client tests.

Deliverables:

- Backend starts locally.
- Health endpoint works.
- Clear-session endpoint works.
- Basic API tests pass.

## Phase 2: Audio Loading and Validation

Tasks:

- Implement audio loader with `librosa.load`.
- Validate duration.
- Preserve full timeline.
- Implement `/api/v1/audio/inspect` returning `AudioInspectResponse` (`file_info` + `pitch_metadata` voiced stats).
- Add `inspect_service.py`.

Deliverables:

- Valid audio metadata and pitch stats returned.
- `no_vocals_detected` on inspect when pitch is too sparse.
- Invalid files produce structured errors.
- Tests cover WAV and generated fixtures.

## Phase 3: Pitch Extraction

Tasks:

- Implement `librosa.pyin` pitch extraction.
- Preserve unvoiced frames.
- Return `PitchFrame` list.
- Add synthetic sine wave tests.
- Add silence preservation tests.

Deliverables:

- Pitch frames include time, F0, confidence, voiced state.
- Silence is represented, not trimmed.

## Phase 4: Compare API (Pitch Only)

Tasks:

- Implement `compare_service`: load both files, extract pitch, package `ComparisonResult`.
- Implement `POST /api/v1/compare` (multipart guru + disciple).
- Optional per-file `PitchSummary` (voiced counts).
- Add integration tests.

Deliverables:

- API returns graph-ready pitch arrays for both recordings.
- `no_vocals_detected` when pitch is too sparse.
- Error cases return structured errors.

## Phase 5: Frontend Shell

Tasks:

- Create PySide6 app.
- Create main window.
- Add `frontend/validation.py` for client-side pre-checks (WAV/MP3/M4A, size, duration).
- Add upload controls.
- Add required Clear button.
- Add compare button.
- Add status and error display.
- Add API client using `httpx`.
- Add error popup behavior.
- Add UI reset after error popup dismissal.

Deliverables:

- App opens.
- Backend health is checked.
- Files can be selected.
- Errors are shown as popups and reset the UI.

## Phase 6: Graph UI

Tasks:

- Implement `pyqtgraph` graph widget.
- Plot guru `frequency_hz` vs `time_seconds`.
- Plot disciple `frequency_hz` vs `time_seconds`.
- Break or omit line segments for unvoiced frames.
- Optional minimal summary (durations / voiced fraction).

Deliverables:

- Successful compare displays dual pitch overlay.
- Y-axis Hz, X-axis seconds.

## Phase 7: Desktop Backend Management

Tasks:

- Start FastAPI backend from frontend app on port **8765**.
- Poll health endpoint at `http://127.0.0.1:8765/api/v1/health`.
- Stop backend on app close.
- Handle backend unavailable state.

Deliverables:

- User can launch desktop app without manually starting backend.

## Phase 8: Packaging

Tasks:

- Create PyInstaller spec.
- Include backend, frontend, and dependencies.
- Include FFmpeg support from `imageio-ffmpeg`.
- Build Windows executable/app folder.
- Smoke test packaged app.

Deliverables:

- Packaged Windows app launches.
- Main comparison workflow works in packaged build.

## Phase 9: Final Verification

Tasks:

- Run automated tests.
- Run manual QA checklist.
- Verify no trimming behavior.
- Verify invalid-file errors.
- Verify app closes cleanly.

Deliverables:

- MVP build ready for review.

## Implementation Order Summary

1. Backend models and health.
2. Audio inspection.
3. Pitch extraction.
4. Compare API (pitch only).
5. Frontend shell.
6. Graph rendering.
7. Backend process management.
8. Packaging.
9. QA.

## Out of scope for MVP (phases to be added later)

Replaces former Phases 4–5 (Sa/swara, alignment/scoring) when scope expands:

| Phase (proposed) | Deliverables |
| --- | --- |
| Sa + swara | `sa_detector`, `swara_mapper`, tests; `guru_sa_hz` / `disciple_sa_hz`; `GET /swara-map` |
| Match + align | `matched_portion_finder`, `aligner`; `MatchedSegment`; `no_matching_pattern` |
| Score + classify | `scorer`, tolerance API/UI; `ComparisonFrame`, `ComparisonMetrics`; match/higher/lower |
| Graph + summary (extended) | Swara Y-axis, matched-only view, `aligned_time`, tolerance band, highlights, score panel |

Also later: tolerance `GET`/`PUT`, processing states for Sa/align/score, highest deviation metric.
