# Architecture

## High-Level Architecture

The MVP is a local desktop app with a Python frontend and Python backend in the same repository.

```txt
PySide6 Desktop App
  |
  | httpx over localhost
  v
FastAPI Backend on 127.0.0.1:8765
  |
  | calls local analysis modules
  v
Audio Analysis Pipeline
  |
  v
Comparison Result JSON
  |
  v
PyQtGraph Visualization
```

## Runtime Components

### Desktop Frontend

Responsibilities:

- Launch or manage backend process.
- Provide single-page UI.
- Select files.
- Run client-side file validation before API calls.
- Validate basic UI state.
- Send files and tolerance to backend.
- Render graph with `pyqtgraph`.
- Show summary metrics and errors.

Libraries:

- `PySide6`
- `pyqtgraph`
- `httpx`

### Local Backend

Responsibilities:

- Expose local FastAPI endpoints.
- Decode and validate audio.
- Run pitch extraction.
- Detect Sa.
- Normalize pitch contours.
- Find similar pitch-contour portions across recordings.
- Align matched contours if needed.
- Exclude non-similar additional portions from comparison and scoring.
- Classify frames.
- Return graph-ready data.

Libraries:

- `FastAPI`
- `uvicorn[standard]`
- `pydantic`
- `python-multipart`
- `librosa`
- `numpy`
- `scipy`
- `soundfile`
- `soxr`
- `imageio-ffmpeg`

## Suggested Repository Structure

```txt
backend/
  app/
    main.py
    api/
      routes_health.py
      routes_audio.py
      routes_compare.py
    models/
      audio.py
      comparison.py
      errors.py
      swara.py
    services/
      audio_loader.py
      pitch_extractor.py
      sa_detector.py
      swara_mapper.py
      matched_portion_finder.py
      aligner.py
      scorer.py
      comparator.py
    core/
      config.py
      errors.py

frontend/
  app.py
  main_window.py
  api_client.py
  backend_manager.py
  validation.py
  widgets/
    upload_panel.py
    tolerance_control.py
    comparison_graph.py
    summary_panel.py
    status_bar.py

shared/
  constants.py

tests/
  backend/
  frontend/
  fixtures/

packaging/
  pyinstaller.spec

requirements.txt
```

## Backend Analysis Pipeline

1. Receive files and tolerance.
2. Decode audio.
3. Validate duration and readability.
4. Load full waveform with `librosa.load(..., mono=True, sr=22050)`.
5. Preserve full waveform. Do not trim silence.
6. Extract F0 with `librosa.pyin`.
7. Preserve frame timeline and mark unvoiced frames.
8. Detect Sa separately for guru and disciple.
9. Convert F0 to cents relative to detected Sa.
10. Map cents to swara labels.
11. Find similar portions with `matched_portion_finder` (sliding windows; see below).
12. Leave non-similar additional portions out of comparison and scoring.
13. Align each `MatchedSegment` with `librosa.sequence.dtw` only (not full files).
14. Build `aligned_frames` with cumulative `aligned_time` across concatenated matched segments.
15. Calculate difference in cents.
16. Classify frames using tolerance (0–25 cents).
17. Calculate summary metrics (`overall_score = total_matching_intervals * 100 / total_intervals`).
18. Return `ComparisonResult` with graph-ready matched-only arrays.

## Sa Detection Strategy

Initial MVP algorithm:

1. Use reliable voiced F0 frames only for Sa estimation.
2. Convert F0 to log-frequency or cents.
3. Fold pitch values into a 1200-cent octave representation.
4. Build a weighted histogram using pitch confidence and stability.
5. Select the dominant stable pitch region as Sa.
6. Return Sa in Hz and optional confidence.

Important rule:

- Excluding unvoiced frames from Sa estimation must not remove them from the internal timeline; the comparison graph displays matched portions only.

### pyin and vocal thresholds (`config.py`)

| Constant | Value | Use |
| --- | --- | --- |
| `SR` | 22050 | Analysis sample rate |
| `HOP_LENGTH` | 220 | ~10 ms frames |
| `FMIN_HZ` / `FMAX_HZ` | 50 / 1000 | `librosa.pyin` range |
| `VOICED_PROB_PLOT_MIN` | 0.55 | Reliable pitch for compare/plot |
| `VOICED_PROB_SILENT_MAX` | 0.35 | Treat as silent/unvoiced |
| `VOICED_PROB_SA_MIN` | 0.65 | Sa estimation only |
| `SA_MIN_VOICED_FRAMES` | 50 | Minimum voiced frames for Sa |
| `SA_HISTOGRAM_MIN_PEAK_WEIGHT` | 0.15 | Below → `sa_detection_failed` |
| `MIN_VOICED_FRAMES_TOTAL` | 30 | Below → `no_vocals_detected` |
| `MIN_VOICED_FRACTION` | 0.05 | Below → `no_vocals_detected` |

Use `no_vocals_detected` only (do not expose `no_pitch_detected`).

## Matched-Portion Discovery

Module: `matched_portion_finder.py` (runs before per-segment DTW).

**Sliding windows:** `min_window_seconds` 1.0, `window_step_seconds` 0.25, `min_voiced_ratio_in_window` 0.40, `min_voiced_frames` 30.

**Coarse match:** Resample voiced `cents_from_sa` in each guru/disciple window pair to length L=50; accept when Pearson `r >= 0.70` and MACE `<= 80` cents, or normalized DTW cost `<= 1.2`.

**Merge:** Adjacent guru windows with gap `< 0.5 s` when disciple mappings overlap.

**`no_matching_pattern` when:** no candidate passes; matched guru voiced duration `< 20%` of guru voiced total; or longest match `< 0.8 s` voiced.

**DTW:** `librosa.sequence.dtw` on raw voiced cents inside each `MatchedSegment` only.

## Graph Rendering Strategy

The backend returns graph-ready arrays. The frontend does not run audio analysis.

Graph data:

- Guru aligned cents.
- Disciple aligned cents.
- `aligned_time` (0…N−1 across concatenated matched segments).
- Guru/disciple original times per frame (debug).
- Matched segments.
- Excluded guru ranges.
- Excluded disciple ranges.
- Classification per frame.
- Swara labels.
- Sa F0 and mapped swara F0 debug values.
- Tolerance band values.

Frontend renders:

- Guru contour line.
- Disciple contour line.
- Tolerance band.
- Match/higher/lower regions.
- Silent/unvoiced gaps.
- Matched comparison portions only.
- Summary metrics.

## Backend Process Management

Recommended MVP:

- Desktop app starts backend as a subprocess on launch.
- Backend binds to `127.0.0.1:8765` (static port).
- Frontend polls `http://127.0.0.1:8765/api/v1/health`.
- Frontend uses the backend tolerance endpoints to get/set tolerance (default 0, range 0–25, step 5).
- Frontend calls the clear-session endpoint when the user clicks Clear; deletes temp files on Clear, error dismiss, and exit.
- Session temp root: e.g. `%TEMP%/hcsa-session/{uuid}/`.
- Frontend shuts down backend process when app exits.

Alternative for later:

- Run FastAPI in an embedded thread if subprocess packaging becomes too complex.

## Packaging

Tool:

- `PyInstaller`.

Packaging requirements:

- Include backend modules.
- Include frontend modules.
- Include `imageio-ffmpeg` binary support.
- Include required Qt/PySide6 resources.
- Produce Windows executable or app folder.

## Security and Privacy

- No cloud calls.
- No login.
- No remote telemetry.
- Backend binds only to localhost.
- Uploaded files are processed locally (WAV and MP3 only).
- Temporary files are deleted on session clear, UI reset after errors, and app exit.

## Later Architecture Extension

Because backend logic is behind FastAPI, future clients can call the same API:

- React frontend.
- Kotlin frontend.
- Separate web UI.
- Remote API deployment, if privacy requirements change later.
