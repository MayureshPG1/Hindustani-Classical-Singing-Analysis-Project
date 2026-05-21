# Architecture

## High-Level Architecture

The MVP is a local desktop app with a Python frontend and Python backend in the same repository.

```txt
PySide6 Desktop App
  |
  | httpx over localhost
  v
FastAPI Backend on 127.0.0.1
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
11. Find similar portions between guru and disciple pitch contours.
12. Leave non-similar additional portions out of comparison and scoring.
13. Align matched pitch contours with `librosa.sequence.dtw` when useful.
14. Calculate difference in cents.
15. Classify frames using tolerance.
16. Calculate summary metrics.
17. Return `ComparisonResult`.

## Sa Detection Strategy

Initial MVP algorithm:

1. Use reliable voiced F0 frames only for Sa estimation.
2. Convert F0 to log-frequency or cents.
3. Fold pitch values into a 1200-cent octave representation.
4. Build a weighted histogram using pitch confidence and stability.
5. Select the dominant stable pitch region as Sa.
6. Return Sa in Hz and optional confidence.

Important rule:

- Excluding unvoiced frames from Sa estimation must not remove them from the graph timeline.

## Graph Rendering Strategy

The backend returns graph-ready arrays. The frontend does not run audio analysis.

Graph data:

- Guru aligned cents.
- Disciple aligned cents.
- Guru original time.
- Disciple original time.
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
- Backend binds to `127.0.0.1` on a configured or available port.
- Frontend polls `/api/v1/health`.
- Frontend uses the backend tolerance endpoints to get/set tolerance.
- Frontend calls the clear-session endpoint when the user clicks Clear or after an error popup is dismissed.
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
- Uploaded files are processed locally.
- Temporary files are cleaned after processing.

## Later Architecture Extension

Because backend logic is behind FastAPI, future clients can call the same API:

- React frontend.
- Kotlin frontend.
- Separate web UI.
- Remote API deployment, if privacy requirements change later.
