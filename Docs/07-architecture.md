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
  | audio_loader + pitch_extractor
  v
ComparisonResult JSON (dual pitch series)
  |
  v
PyQtGraph Visualization (Hz vs time)
```

## Runtime Components

### Desktop Frontend

Responsibilities:

- Launch or manage backend process.
- Provide single-page UI.
- Select files.
- Run client-side file validation before API calls.
- Send both files to compare endpoint.
- Render dual F0 contours with `pyqtgraph`.
- Show optional lightweight summary and errors.

Libraries:

- `PySide6`
- `pyqtgraph`
- `httpx`

### Local Backend

Responsibilities:

- Expose local FastAPI endpoints.
- Decode and validate audio.
- Run pitch extraction with `librosa.pyin`.
- Return pitch frame arrays for guru and disciple.
- Enforce minimum voiced content (`no_vocals_detected`).

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
    services/
      audio_loader.py
      pitch_extractor.py
      inspect_service.py
      compare_service.py
    core/
      config.py
      errors.py
      session.py

frontend/
  app.py
  main_window.py
  api_client.py
  backend_manager.py
  validation.py
  widgets/
    upload_panel.py
    comparison_graph.py
    status_bar.py

shared/

tests/
  backend/
  frontend/
  fixtures/

packaging/
  pyinstaller.spec

requirements.txt
```

Legacy modules (`sa_detector`, `swara_mapper`, `matched_portion_finder`, `aligner`, `scorer`, `comparator`, `swara` model) may exist in the repo during transition; they are not part of the minimal MVP architecture and should be removed when code is updated.

## Backend Analysis Pipeline

1. Receive guru and disciple files.
2. Decode audio.
3. Validate duration and readability.
4. Load full waveform: WAV via `librosa.load`; MP3/M4A via bundled `imageio-ffmpeg` (`backend/app/core/ffmpeg.py`).
5. Preserve full waveform. Do not trim silence.
6. Extract F0 with `librosa.pyin` for each file.
7. Preserve frame timeline and mark unvoiced frames.
8. Optionally compute per-file voiced counts for summary.
9. Return `ComparisonResult` with `guru_pitch_frames` and `disciple_pitch_frames`.

### pyin and vocal thresholds (`config.py`)

| Constant | Value | Use |
| --- | --- | --- |
| `SR` | 22050 | Analysis sample rate |
| `HOP_LENGTH` | 512 | ~23 ms frames |
| `PYIN_CHUNK_SECONDS` | 15 | Chunk size for verbose `pyin progress` percent logs |
| `FMIN_HZ` / `FMAX_HZ` | 50 / 1000 | `librosa.pyin` range |
| `VOICED_PROB_PLOT_MIN` | 0.55 | Reliable pitch for plotting |
| `VOICED_PROB_SILENT_MAX` | 0.35 | Treat as silent/unvoiced |
| `MIN_VOICED_FRAMES_TOTAL` | 30 | Below → `no_vocals_detected` |
| `MIN_VOICED_FRACTION` | 0.05 | Below → `no_vocals_detected` |
| `INSPECT_PITCH_PREVIEW_FRAMES` | 5 | Frames in inspect `preview_frames` |

Use `no_vocals_detected` only (do not expose `no_pitch_detected`).

Sa-specific constants (`VOICED_PROB_SA_MIN`, `SA_*`) are not used in minimal MVP.

## Inspect vs Compare

- **Inspect:** load → pyin (full timeline for stats) → `AudioInspectResponse` with `file_info` and `pitch_metadata` (**5** preview frames only).
- **Compare:** load both files → pyin → full `guru_pitch_frames` and `disciple_pitch_frames`.

## Graph Rendering Strategy

The backend returns pitch arrays. The frontend does not run audio analysis.

Graph data per series:

- X: `time_seconds`
- Y: `frequency_hz` (plot only when voiced and above confidence threshold; gaps elsewhere)

Frontend renders:

- Guru contour line.
- Disciple contour line.
- Legend distinguishing guru vs disciple.
- No tolerance band, classification colors, or swara axis labels in MVP.

## Backend Process Management

Recommended MVP:

- Desktop app starts backend as a subprocess on launch.
- Backend binds to `127.0.0.1:8765` (static port).
- Frontend polls `http://127.0.0.1:8765/api/v1/health`.
- Frontend calls the clear-session endpoint when the user clicks Clear; deletes temp files on Clear, error dismiss, and exit.
- Session temp root: e.g. `%TEMP%/hcsa-session/{uuid}/`.
- Frontend shuts down backend process when app exits.

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
- Uploaded files are processed locally (WAV, MP3, and M4A).
- Temporary files are deleted on session clear, UI reset after errors, and app exit.

## Out of scope for MVP (architecture to be added later)

Modules and pipeline steps removed from minimal MVP (may exist in repo until code cleanup):

| Module / step | Role when added |
| --- | --- |
| `sa_detector.py` | Histogram-based Sa per recording |
| `swara_mapper.py` | Cents → swara label/symbol |
| `matched_portion_finder.py` | Sliding-window similar portions |
| `aligner.py` | DTW per `MatchedSegment` |
| `scorer.py` | Tolerance classification and metrics |
| `comparator.py` | Orchestrate full Hindustani pipeline |
| `models/swara.py` | Swara map API model |

Pipeline steps to re-insert after pitch extraction: detect Sa → cents-from-Sa → swara map → find portions → DTW → classify → metrics.

Graph (later): cents/swara Y-axis, matched-only X-axis, tolerance band, classification colors.

Because backend logic is behind FastAPI, future clients can call the same API:

- React frontend.
- Kotlin frontend.
- Separate web UI.
