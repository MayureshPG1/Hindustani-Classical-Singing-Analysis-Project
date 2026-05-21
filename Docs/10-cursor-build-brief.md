# Cursor Build Brief

## Mission

Build the MVP local Windows desktop app described in the spec pack. The app compares a guru vocal recording with a disciple vocal recording, normalizes each to detected Sa, and displays pitch-contour comparison as a graph with statistics.

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
- Preserve full uploaded timeline in backend analysis (no trimming).
- Do not trim silence, non-vocal sections, or long endings during load/analysis.
- Guru and disciple clips may have different durations.
- Find similar portions and compare only those portions.
- Leave non-similar additional portions out of comparison and scoring.
- Graph displays **matched portions only**; X-axis is concatenated alignment index.
- Guru and disciple may sing in different absolute scales.
- Compare pitch relative to detected Sa.
- Supported formats: **WAV and MP3 only** (no M4A).
- Errors must be shown as popups.
- After an error popup is dismissed, reset the UI, delete temp files, and start again.
- Client-side file validation before API inspect.
- Required **Clear** button; deletes temps and resets tolerance to 0.
- Defer graph hover/zoom.
- Fixed 100-cent swara bins (no shruti nuance in MVP).
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
- `imageio-ffmpeg` (MP3 decode in packaged app)

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

1. Upload guru audio (WAV/MP3).
2. Upload disciple audio (WAV/MP3).
3. Client-side then API validation for both files.
4. Set tolerance: default **0** cents, range **0–25**, step **5** cents.
5. Compare files through local FastAPI backend at `http://127.0.0.1:8765/api/v1`.
6. Extract pitch using `librosa.pyin` with thresholds in `07-architecture.md`.
7. Auto-detect Sa separately for guru and disciple.
8. Normalize pitch contours relative to Sa.
9. Map swaras using `S r R g G m M P d D n N` (100-cent bins).
10. Find similar portions with `matched_portion_finder`; DTW per `MatchedSegment` only.
11. Handle different-duration clips via matched-portion discovery.
12. Exclude non-similar portions from comparison, scoring, and graph.
13. Classify frames as match, higher, lower, or unknown.
14. Return specific errors for no audio, no vocals, no Sa, no matching pattern, and comparison failure.
15. Show graph with guru/disciple contours, tolerance band, highlights (matched regions only).
16. Show statistics; `overall_score = total_matching_intervals * 100 / total_intervals`.
17. Clear button and session/temp cleanup.

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

## Suggested First Implementation Slice

Build the backend first:

1. Create project structure.
2. Add FastAPI health endpoint (port 8765).
3. Add Pydantic models.
4. Add tolerance get/set endpoints (0–25, default 0, step 5).
5. Add clear-session endpoint (delete temp files).
6. Add audio loader (WAV/MP3).
7. Add pitch extractor with config thresholds.
8. Add Sa detector.
9. Add swara mapper.
10. Add matched-portion finder.
11. Add aligner (DTW per segment).
12. Add scorer.
13. Add compare endpoint.
14. Add tests with synthetic audio.

Then build frontend:

1. Main PySide6 window.
2. `validation.py` client checks.
3. Upload controls.
4. Tolerance control (0, ±5).
5. API client.
6. Graph widget (matched-only, concatenated X).
7. Summary panel.
8. Error popups with UI reset and temp delete.
9. Clear button.
10. Backend process management on port 8765.

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
- User can upload guru and disciple WAV/MP3 files.
- Compare produces matched-only graph and statistics.
- Different scales normalized relative to Sa.
- Different-duration clips compare when similar portions exist.
- Extra non-similar portions excluded from scoring.
- Invalid files and analysis failures produce popup errors and reset UI with temp cleanup.
- Backend API tests pass.
- Core analysis unit tests pass.
- Packaged Windows build can be produced.
