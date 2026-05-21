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
- Backend binds only to localhost.
- Single-page UI.
- No audio playback.
- No live recording.
- No real-time feedback.
- No export.
- No detailed rhythm/taal feedback.
- No coaching text.
- Preserve full uploaded timeline.
- Do not trim silence, non-vocal sections, or long endings.
- Guru and disciple clips may have different durations.
- Find similar portions and compare only those portions.
- Leave non-similar additional portions out of comparison and scoring.
- Guru and disciple may sing in different absolute scales.
- Compare pitch relative to detected Sa.
- Errors must be shown as popups.
- After an error popup is dismissed, reset the UI so the user starts from the beginning.

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
- `imageio-ffmpeg`

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

1. Upload guru audio.
2. Upload disciple audio.
3. Validate both files.
4. Set tolerance with default 50 cents.
5. Plus/minus tolerance step is 10 cents.
6. Compare files through local FastAPI backend.
7. Extract pitch using `librosa.pyin`.
8. Auto-detect Sa separately for guru and disciple.
9. Normalize pitch contours relative to Sa.
10. Map swaras using `S r R g G m M P d D n N`.
11. Align contours with `librosa.sequence.dtw` where useful.
12. Handle different-duration clips by finding similar portions.
13. Exclude non-similar additional portions from comparison and scoring.
14. Classify frames as match, higher, lower, or unknown.
15. Return specific errors for no audio, no vocals, no Sa, no matching pattern, and comparison failure.
16. Show graph with guru contour, disciple contour, tolerance band, and highlighted comparison regions.
17. Show statistics.

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
2. Add FastAPI health endpoint.
3. Add Pydantic models.
4. Add tolerance get/set endpoints.
5. Add clear-session endpoint.
6. Add audio loader.
7. Add pitch extractor.
8. Add Sa detector.
9. Add swara mapper.
10. Add matched-portion discovery.
11. Add scorer.
12. Add compare endpoint.
13. Add tests with synthetic audio.

Then build frontend:

1. Main PySide6 window.
2. Upload controls.
3. Tolerance control.
4. API client.
5. Graph widget.
6. Summary panel.
7. Error popups with UI reset after dismissal.
8. Backend process management.

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

- App launches locally.
- User can upload guru and disciple files.
- Compare produces graph and statistics.
- Different scales are normalized relative to Sa.
- Different-duration clips compare successfully when they contain similar portions.
- Extra non-similar portions are excluded from scoring.
- Silence and endings are preserved.
- Invalid files and analysis failures produce popup errors and reset the UI.
- Backend API tests pass.
- Core analysis unit tests pass.
- Packaged Windows build can be produced.
