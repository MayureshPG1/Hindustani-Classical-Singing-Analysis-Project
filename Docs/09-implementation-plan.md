# Implementation Plan

## Build Strategy

Build the product in vertical slices. Start with backend analysis correctness, then API, then frontend graph display, then packaging.

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
- Add tolerance get/set endpoints.
- Add clear-session endpoint.
- Add Pydantic models.
- Add structured error model.
- Add test client tests.

Deliverables:

- Backend starts locally.
- Health endpoint works.
- Tolerance and clear-session endpoints work.
- Basic API tests pass.

## Phase 2: Audio Loading and Validation

Tasks:

- Implement audio loader with `librosa.load`.
- Validate duration.
- Preserve full timeline.
- Return `AudioFileInfo`.
- Implement `/api/v1/audio/inspect`.

Deliverables:

- Valid audio metadata returned.
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

## Phase 4: Sa Detection and Swara Mapping

Tasks:

- Implement Sa detection from reliable pitch frames.
- Implement cents-from-Sa conversion.
- Implement swara mapping table.
- Add unit tests for Sa detection and swara mapping.

Deliverables:

- Guru and disciple Sa can be detected separately.
- Different scales normalize correctly.
- Swara symbols match PRD mapping.

## Phase 5: Alignment and Scoring

Tasks:

- Implement matched-portion discovery for different-duration recordings.
- Implement DTW alignment with `librosa.sequence.dtw`.
- Preserve original guru/disciple times.
- Exclude non-similar additional portions from comparison and scoring.
- Implement tolerance classification.
- Implement summary metrics.
- Add tests for match/higher/lower/unknown.
- Add tests for different-duration clips and no matching pattern.

Deliverables:

- Comparison frames generated.
- Matched segments and excluded ranges generated.
- Metrics generated.
- Known synthetic offsets classify correctly.
- No matching pattern returns a specific error.

## Phase 6: Compare API

Tasks:

- Implement `POST /api/v1/compare`.
- Accept guru file, disciple file, and tolerance.
- Run full analysis pipeline.
- Return `ComparisonResult`.
- Add integration tests.

Deliverables:

- API returns graph-ready comparison data.
- Error cases return structured errors.

## Phase 7: Frontend Shell

Tasks:

- Create PySide6 app.
- Create main window.
- Add upload controls.
- Add tolerance control.
- Add compare button.
- Add status and error display.
- Add API client using `httpx`.
- Add error popup behavior.
- Add UI reset after error popup dismissal.

Deliverables:

- App opens.
- Backend health is checked.
- Files can be selected.
- Tolerance control works.
- Errors are shown as popups and reset the UI.

## Phase 8: Graph and Summary UI

Tasks:

- Implement `pyqtgraph` graph widget.
- Render guru and disciple contours.
- Render tolerance band.
- Render match/higher/lower regions.
- Render unvoiced gaps.
- Render summary panel.

Deliverables:

- Successful compare displays graph and metrics.
- Graph uses Indian swara labels.

## Phase 9: Desktop Backend Management

Tasks:

- Start FastAPI backend from frontend app.
- Poll health endpoint.
- Stop backend on app close.
- Handle backend unavailable state.

Deliverables:

- User can launch desktop app without manually starting backend.

## Phase 10: Packaging

Tasks:

- Create PyInstaller spec.
- Include backend, frontend, and dependencies.
- Include FFmpeg support from `imageio-ffmpeg`.
- Build Windows executable/app folder.
- Smoke test packaged app.

Deliverables:

- Packaged Windows app launches.
- Main comparison workflow works in packaged build.

## Phase 11: Final Verification

Tasks:

- Run automated tests.
- Run manual QA checklist.
- Verify no trimming behavior.
- Verify different-scale comparison.
- Verify invalid-file errors.
- Verify app closes cleanly.

Deliverables:

- MVP build ready for review.

## Implementation Order Summary

1. Backend models and health.
2. Audio inspection.
3. Pitch extraction.
4. Sa detection.
5. Swara mapping.
6. Alignment and scoring.
7. Compare API.
8. Frontend shell.
9. Graph rendering.
10. Backend process management.
11. Packaging.
12. QA.
