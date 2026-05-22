# Cursor Build Brief

## Mission

Build the MVP local Windows desktop app described in the spec pack. The app compares a guru vocal recording with a disciple vocal recording by extracting F0 with `librosa.pyin` and displaying both pitch contours on one graph (Hz vs wall-clock time).

## Source of Truth

Read these docs before implementation:

1. `00-project-context.md`
2. `01-prd.md`
3. `02-user-journeys.md`
4. `03-functional-spec.md`
5. `04-ux-spec.md`
6. `05-data-model.md`
7. `06-api-spec.md`
8. `07-architecture.md`
9. `08-test-plan.md`
10. `09-implementation-plan.md`

## Non-Negotiable MVP Constraints

- Windows desktop first.
- Python `3.11.x`.
- Local-only processing.
- No cloud calls.
- Backend binds only to localhost on port **8765**.
- Single-page UI.
- No audio playback.
- No live recording.
- No real-time feedback.
- No export.
- No detailed rhythm/taal feedback.
- No coaching text.
- Preserve full uploaded timeline in pitch extraction (no trimming).
- Do not trim silence, non-vocal sections, or long endings during load/analysis.
- Guru and disciple clips may have different durations.
- Graph plots **full-timeline** F0 for both files on **wall-clock** `time_seconds`.
- Y-axis: **Hz** (linear).
- No Sa detection, swara mapping, DTW, matched portions, or tolerance scoring in MVP.
- Supported formats: **WAV, MP3, and M4A**.
- Errors must be shown as popups.
- After an error popup is dismissed, reset the UI, delete temp files, and start again.
- Client-side file validation before API inspect.
- Required **Clear** button; deletes temps on clear and error dismiss.
- Defer graph hover/zoom.
- Use `no_vocals_detected` only (no `no_pitch_detected`).

## Final Library Choices

Backend:

- `FastAPI`
- `uvicorn[standard]`
- `pydantic`
- `python-multipart`

Audio:

- `librosa==0.11.0`
- `numpy`
- `scipy`
- `soundfile==0.13.1`
- `soxr`
- `imageio-ffmpeg` (MP3/M4A decode in packaged app)

Frontend:

- `PySide6`
- `pyqtgraph`
- `httpx`

Packaging:

- `pyinstaller`

Testing:

- `pytest`
- `pytest-qt`
- `pytest-cov`

## Required MVP Features

1. Upload guru audio (WAV/MP3/M4A).
2. Upload disciple audio (WAV/MP3/M4A).
3. Client-side then API validation for both files (`inspect` returns `file_info` + pitch voiced stats).
4. Compare files through local FastAPI backend at `http://127.0.0.1:8765/api/v1`.
5. Extract pitch using `librosa.pyin` with thresholds in `07-architecture.md`.
6. Return `guru_pitch_frames` and `disciple_pitch_frames` from `POST /compare`.
7. Show dual F0 graph (Hz vs time).
8. Return specific errors for no audio, no vocals, and comparison failure.
9. Clear button and session/temp cleanup.

## Suggested First Implementation Slice

Build the backend first:

1. Create project structure.
2. Add FastAPI health endpoint (port 8765).
3. Add Pydantic models (slim `PitchFrame`, `ComparisonResult`).
4. Add clear-session endpoint (delete temp files).
5. Add audio loader (WAV/MP3/M4A).
6. Add pitch extractor with config thresholds.
7. Add compare service and compare endpoint.
8. Add tests with synthetic audio.

Then build frontend:

1. Main PySide6 window.
2. `validation.py` client checks.
3. Upload controls.
4. API client.
5. Graph widget (dual Hz vs time).
6. Error popups with UI reset and temp delete.
7. Clear button.
8. Backend process management on port 8765.

Then package:

1. PyInstaller spec.
2. Packaged smoke test.

## Expected Repository Shape

```txt
backend/
frontend/
shared/
tests/
packaging/
requirements.txt
```

## Definition of Done

- App launches locally; backend on `127.0.0.1:8765`.
- User can upload guru and disciple WAV/MP3/M4A files.
- Compare returns pitch arrays and displays dual contour graph.
- Invalid files and analysis failures produce popup errors and reset UI with temp cleanup.
- Backend API tests pass.
- Core pitch extraction unit tests pass.
- Packaged Windows build can be produced.

## Out of scope for MVP (do not build unless requested)

**Sa and swaras:** `sa_detector`, `swara_mapper`, `models/swara.py`, `shared` swara table, `GET /swara-map`, cents-from-Sa, swara fields on `PitchFrame`, swara Y-axis.

**Matching and alignment:** `matched_portion_finder`, `aligner`, `comparator` (full pipeline), DTW, matched-only graph, `aligned_time`, `matched_segments`, `excluded_*_ranges`, `aligned_frames`, `no_matching_pattern`.

**Tolerance and scoring:** tolerance UI (0–25, step 5), `GET`/`PUT /settings/tolerance`, `scorer`, `ComparisonMetrics`, match/higher/lower/unknown classification, tolerance band and graph highlights, `overall_score` and percentage summary, `invalid_tolerance`, `sa_detection_failed`.

**Other:** highest deviation metric; log-scale Hz Y-axis (optional later).
