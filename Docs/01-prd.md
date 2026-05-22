# Product Requirements Document: Hindustani Classical Music Learning App

## 1. Product Summary

The product is a local desktop application for Hindustani classical music learning. It allows a guru to upload a recorded audio file and a disciple to upload their own recorded version of the same musical phrase, exercise, bandish segment, raga phrase, taan, alap, or swara practice. The app compares both recordings by extracting pitch (F0) from each file and presenting a graphical overlay of guru and disciple pitch contours over time (Hz vs seconds).

The first version will be a single-page desktop app with three core actions:

1. Upload guru audio.
2. Upload disciple audio.
3. Compare and view graphical analysis.

The app should primarily use Python for the backend/audio-analysis logic and should run locally as a compiled desktop application. No cloud upload should be required for the MVP. The first implementation will keep the backend API and frontend app in the same repository as one local app, but the backend should be designed as a FastAPI service so a future React, Kotlin, or other frontend can reuse the same analysis API.

## 2. Problem Statement

In Hindustani classical music training, disciples often learn by listening to a guru and attempting to reproduce phrases accurately. Feedback usually depends on live correction from the guru. When practicing alone, disciples do not have an easy way to see whether their pitch movement, note placement, and melodic shape match the guru's reference.

The app solves this by comparing two recorded audio files and creating a visual overlay of the guru's and disciple's pitch contours. The disciple can see:

- Both melodic shapes side by side on one graph.
- Where pitch rises, falls, or is silent in each recording.
- How their contour relates visually to the guru's reference (shape and timing at a glance).

Automatic match/higher/lower scoring and Sa-relative normalization are deferred to later versions.

## 3. Target Users

### Primary User: Disciple or Student

- Practices Hindustani classical vocal music.
- Records their own attempt after listening to a guru's reference.
- Wants clear, visual analysis without needing technical audio knowledge.
- May be a beginner, intermediate learner, or advanced learner working on precision.

### Secondary User: Guru or Teacher

- Records or provides reference audio.
- May use the app during lessons or assign practice outside lessons.
- Wants students to identify mistakes before the next class.

## 4. Product Goals

- Provide a simple local tool for comparing a guru's vocal recording with a disciple's vocal recording.
- Make pitch differences understandable through a graphical overlay.
- Keep the UI extremely simple and focused on the comparison workflow.
- Support offline use and local processing.
- Build the audio-analysis backend primarily in Python.
- Create a desktop app that can be compiled and distributed locally.

## 5. Non-Goals for MVP

- No social network, user profiles, or lesson management.
- No cloud storage or remote file syncing.
- No marketplace for gurus or students.
- No multi-page navigation.
- No automatic raga teaching curriculum in the first version.
- No live real-time singing feedback in the first version.
- No direct microphone recording in the first version.
- No audio playback inside the app in the first version.
- No export of graph or reports in the first version.
- No detailed rhythm, taal, or timing analysis in the first version.
- No mobile app in the first version unless later prioritized.
- No full transcription into notation as a required MVP feature.

### Removed from minimal MVP (to be added later)

See also §18 To Be Done Later. Not in scope for the current pitch-overlay MVP:

- **Sa and swaras:** auto-detect Sa per file; cents-from-Sa; swara labels/symbols on graph; `GET /swara-map`.
- **Alignment and matching:** matched-portion finder; DTW per segment; compare only matched regions; `aligned_frames` and concatenated `aligned_time` on the graph.
- **Scoring:** tolerance control (0–25 cents); match/higher/lower/unknown classification; tolerance band and colored regions on graph; `overall_score` and deviation/match percentages; exclude non-similar portions from metrics.
- **API/data:** `guru_sa_hz`, `disciple_sa_hz`, `matched_segments`, `excluded_*_ranges`, `ComparisonMetrics`; errors `sa_detection_failed`, `no_matching_pattern`, `invalid_tolerance`; `GET`/`PUT /settings/tolerance`.

## 6. Core User Flow

1. User opens the desktop app.
2. User clicks "Upload Guru Voice" and selects an audio file.
3. App validates the file and displays basic file information.
4. User clicks "Upload Disciple Voice" and selects an audio file.
5. App validates the file and displays basic file information.
6. User clicks "Compare".
7. App processes both audio files locally and extracts pitch for each.
8. App displays an overlay graph: guru and disciple F0 (Hz) vs wall-clock time.
9. User inspects the dual pitch contours (optional lightweight file summary such as duration or voiced fraction).

## 7. MVP User Interface Requirements

The MVP is a single-page desktop UI.

### Required Controls

- Button: "Upload Guru Voice"
- Button: "Upload Disciple Voice"
- Button: "Compare"
- Button: "Clear" (resets session, deletes temp files)

Tolerance controls are not part of MVP.

### Required Display Areas

- Guru file status:
  - File name
  - Duration
  - Format
  - Validation status

- Disciple file status:
  - File name
  - Duration
  - Format
  - Validation status

- Processing status:
  - Idle
  - Loading audio
  - Extracting pitch
  - Generating graph
  - Complete
  - Error

- Comparison graph:
  - Guru pitch contour (Hz vs time)
  - Disciple pitch contour (Hz vs time)
  - Full timeline per recording

- Optional summary (not scored):
  - File durations
  - Voiced frame count or voiced fraction per file

### UI Principles

- The app should feel like a practical practice tool, not a complex studio editor.
- The first screen should be the actual upload and comparison interface.
- No onboarding page is required for MVP.
- All important actions should be visible without navigation.
- Visual analysis should be understandable to a non-technical music student.
- UI language for MVP shall be English.

## 8. Audio Input Requirements

### Supported File Types for MVP

Recommended MVP support:

- WAV
- MP3
- M4A

### File Constraints

Initial assumptions:

- Maximum audio length: 5 minutes per file for MVP.
- Recommended recording length: 10 seconds to 5 minutes.
- Mono and stereo files should both be accepted.
- Files should be converted internally to mono for analysis.
- Sample rate should be normalized internally, likely to 22050 Hz or 44100 Hz.

### Validation

The app should detect and show clear errors for:

- Unsupported file type.
- Empty or unreadable file.
- Audio file with no detectable vocal pitch.
- File duration too long.
- No usable audio data.
- No vocals detected.

Guru and disciple clips may have different durations as long as each file is 5 minutes or shorter. Different durations should not block comparison by themselves.

## 9. Audio Analysis Requirements

The comparison focuses on vocal pitch contour extraction and dual overlay visualization. The MVP does not align phrases with DTW, classify match/higher/lower, or provide rhythm, taal, or timing feedback.

### 9.1 Preprocessing

The app should:

- Load both audio files locally.
- Convert stereo to mono.
- Normalize sample rate.
- Normalize loudness for analysis purposes.
- Preserve the full uploaded audio duration, including leading silence, trailing silence, long endings, and non-vocal silent sections.
- Do not trim or remove long endings.
- Do not remove non-vocal silent sections from the timeline.
- Mark unvoiced or silent regions as unvoiced in the analysis instead of deleting them.

Implementation library decision:

- Use `librosa.load(..., mono=True, sr=22050)` as the primary audio loading path.
- Use `soundfile` as the primary file-reading backend used by `librosa`.
- Bundle FFmpeg support through `imageio-ffmpeg` so MP3 and M4A decoding is reliable in the packaged Windows app.
- Use NumPy arrays as the internal audio representation.
- Do not call trimming helpers such as silence trimming; preserve the full loaded waveform and full time axis.

### 9.2 Pitch Extraction

The app should extract the fundamental frequency, also called F0, from both recordings over time.

Recommended approach:

- Use `librosa.pyin` as the primary MVP pitch extraction method.
- Extract pitch at small time intervals, for example every 10 ms to 20 ms.
- Store confidence values for each detected pitch frame.
- Ignore frames with very low pitch confidence.

Justification:

- `librosa.pyin` implements probabilistic YIN, which is suitable for monophonic vocal pitch tracking.
- It returns F0 values, voiced/unvoiced flags, and voiced probabilities, which map directly to the app's need to preserve silent/unvoiced timeline regions.
- It keeps the MVP dependency set smaller than neural pitch trackers such as CREPE/torchcrepe.
- `torchcrepe` can be evaluated later if `librosa.pyin` is not accurate enough for noisy vocal recordings, but it is not part of the MVP dependency set.

### 9.3 Pitch Representation (MVP)

MVP uses raw frequency in Hz for graph display:

- Each `PitchFrame` has `time_seconds` and optional `frequency_hz`.
- Unvoiced or low-confidence frames keep timeline position but omit F0 from the plotted line.
- Y-axis: Hz (linear). X-axis: seconds from the start of each recording.

Guru and disciple may sing in different keys; the overlay does not normalize to Sa in MVP. Users compare shape visually; cross-key normalization is later scope.

### 9.4 Audio Analysis Library Plan

The MVP audio backend uses `librosa` for load, resample, and `librosa.pyin` F0 extraction. UI uses `PySide6` and `pyqtgraph`.

| PRD Task | Final Library Choice | Justification |
| --- | --- | --- |
| Load audio | `librosa.load`, `soundfile`, `imageio-ffmpeg` | Reliable local decode for WAV/MP3/M4A in packaged Windows app. |
| Preserve silence and endings | Custom logic with `numpy` arrays | Full timeline preserved; no trimming helpers. |
| Mono conversion | `librosa.load(..., mono=True)` | Consistent mono analysis path. |
| Resampling | `librosa.load(..., sr=22050)` with `soxr` | Predictable analysis rate. |
| Pitch/F0 extraction | `librosa.pyin` | F0, voiced flags, and voiced probability for vocals. |
| Graph display | `pyqtgraph` | Native Qt plotting with `PySide6`. |

Recommended audio-comparison pipeline:

1. Decode input audio to PCM.
2. Load full audio without trimming.
3. Convert to mono and resample to `22050 Hz`.
4. Run `librosa.pyin` with `fmin=50 Hz` and `fmax=1000 Hz`.
5. Build `PitchFrame` list per file (full timeline).
6. Return both series in `ComparisonResult`.
7. Frontend plots guru and disciple Hz vs `time_seconds`.

Deferred: Sa detection, swara mapping, matched-portion finder, DTW, tolerance scoring.

## 10. Graphical Analysis Requirements

The graph is the primary output of the app.

### Required Graph Elements

- X-axis: `time_seconds` (wall-clock from start of each recording).
- Y-axis: frequency in Hz (linear).
- Guru line: one clear color.
- Disciple line: second clear color.
- Gaps or unvoiced areas: visible breaks where F0 is not plotted.
- Full pitch timeline for each uploaded file.

### Deferred Graph Elements (Later Scope)

- Indian swara Y-axis labels.
- Tolerance band and match/higher/lower highlights.
- Matched-portions-only view and concatenated alignment index.
- Hover tooltips.
- Zoom and pan.

### Optional Summary (Not Scored)

- Guru and disciple duration.
- Voiced frame count or voiced fraction per file.

## 11. Desktop App Requirements

### Recommended Architecture

The app should use a local API-based desktop architecture:

- Python FastAPI backend for audio upload, validation, analysis, and comparison.
- Python desktop frontend app for file selection, graph display, and optional lightweight summary.
- Shared local repository for frontend and backend in the MVP.
- Local file processing only.
- API boundary designed so the backend can later serve other frontends, such as React or Kotlin.

Finalized MVP technology choices:

1. Python `3.11.x` for the backend, frontend, and packaging environment.
2. `FastAPI` for the local Python backend API.
3. `uvicorn[standard]` for running the local API process during development and inside the packaged app.
4. `pydantic` for API request and response schemas.
5. `python-multipart` for local upload-style file handling through FastAPI.
6. `httpx` for the Python desktop frontend to call the local FastAPI backend.
7. `PySide6` for the Python desktop frontend.
8. `pyqtgraph` for graph rendering.
9. `librosa` as the core audio-analysis and music-information-retrieval library.
10. `numpy` and `scipy` for numerical processing and optional smoothing/filtering operations.
11. `soundfile` for audio file reading support used by `librosa`.
12. `soxr` for high-quality resampling through `librosa`.
13. `imageio-ffmpeg` to package FFmpeg support for MP3 and M4A decoding on Windows.
14. `PyInstaller` for compiling into a local Windows desktop executable.

Recommended MVP choice:

- Use `librosa` as the main DSP engine rather than mixing multiple pitch/audio-analysis libraries in MVP.
- Keep MVP backend logic limited to load, validate, and pitch extraction; defer Sa, swara, alignment, and scoring.
- Use `PySide6` plus `pyqtgraph` for the frontend and graph instead of Matplotlib or Plotly.
- Use `PyInstaller` instead of Nuitka for the first packaging pass.
- Keep `praat-parselmouth`, `pyworld`, `Essentia`, `CREPE`, and `torchcrepe` out of the MVP dependency set unless pitch accuracy testing proves `librosa.pyin` is insufficient.

### Dependency Groups

The MVP should organize dependencies by responsibility so the backend can later be reused by non-Python frontends.

Backend API dependencies:

- `fastapi`
- `uvicorn[standard]`
- `pydantic`
- `python-multipart`

Audio-analysis dependencies:

- `librosa==0.11.0`
- `numpy`
- `scipy`
- `soundfile==0.13.1`
- `soxr`
- `imageio-ffmpeg`

Frontend dependencies:

- `PySide6`
- `pyqtgraph`
- `httpx`

Packaging dependencies:

- `pyinstaller`

Testing dependencies:

- `pytest`
- `pytest-qt`
- `pytest-cov`

Recommended dependency file for the first implementation:

```txt
fastapi
uvicorn[standard]
pydantic
python-multipart
httpx

librosa==0.11.0
numpy
scipy
soundfile==0.13.1
soxr
imageio-ffmpeg

PySide6
pyqtgraph

pyinstaller
pytest
pytest-qt
pytest-cov
```

### Dependency Relationships

- `FastAPI` depends on `Starlette` for the web layer and `Pydantic` for data validation and serialization.
- `uvicorn` runs the local FastAPI ASGI app.
- `httpx` is used by the Python desktop frontend to call the local API.
- `librosa` uses `numpy` and `scipy` for numerical processing and depends on audio I/O/resampling support such as `soundfile` and `soxr`.
- `soundfile` is based on libsndfile and is used for reading sampled audio files.
- `imageio-ffmpeg` provides an FFmpeg executable in platform-specific wheels, useful for packaged Windows decoding support.
- `PyQtGraph` is built on Qt bindings and NumPy; in this app it uses `PySide6` as the Qt binding.
- `PyInstaller` bundles the Python application and its dependencies into a Windows distributable.

### Libraries Explicitly Not Chosen for MVP

- `praat-parselmouth`: strong voice-analysis library and direct Praat wrapper, but it is GPLv3 and may complicate app licensing/distribution. It also does not solve alignment or graph rendering.
- `pyworld`: useful for speech analysis/synthesis workflows, but it is not needed for the first pitch-contour comparison pipeline.
- `Essentia`: powerful audio-analysis library, but heavier and potentially more complex to package on Windows for this MVP.
- `CREPE` / `torchcrepe`: useful neural pitch trackers, but add model and PyTorch packaging complexity. Keep as later evaluation if `librosa.pyin` is not accurate enough.
- Matplotlib: useful for static plots, but `pyqtgraph` is a better fit for an interactive desktop overlay graph.
- Plotly: good for web graphs, but less natural for a native Python desktop app than `pyqtgraph`.
- Nuitka: possible later, but `PyInstaller` is the first packaging choice because it is straightforward for Windows desktop distribution.

### Backend API Requirements

The backend shall expose local API endpoints for the frontend to use. Exact route names may change during implementation, but the API should support:

- Health check.
- Guru audio upload/selection metadata.
- Disciple audio upload/selection metadata.
- Compare request with guru file and disciple file.
- Compare response containing `guru_pitch_frames` and `disciple_pitch_frames` for graphing.
- Error responses for invalid file, unsupported format, missing pitch, and analysis failure.

### Frontend App Requirements

The frontend shall be a Python desktop app in the MVP.

Requirements:

- Shows the single-page upload and comparison UI.
- Sends analysis requests to the local FastAPI backend.
- Displays the graph and statistics returned by the backend.
- Does not contain core audio-analysis logic.
- Can later be replaced by another frontend without rewriting the backend analysis engine.

### Local Processing

- Audio files must remain on the user's machine.
- No login should be required.
- No internet connection should be required for core comparison.
- The local FastAPI server should bind only to localhost in the MVP.
- Temporary files should be cleaned up after processing.

## 12. Functional Requirements

### FR-1: Upload Guru Audio

The app shall allow the user to select a guru audio recording from local storage.

Acceptance criteria:

- User can click "Upload Guru Voice".
- System opens a local file picker.
- System accepts supported audio file formats.
- System displays file name and duration after successful upload.
- System shows a useful error if the file cannot be loaded.

### FR-2: Upload Disciple Audio

The app shall allow the user to select a disciple audio recording from local storage.

Acceptance criteria:

- User can click "Upload Disciple Voice".
- System opens a local file picker.
- System accepts supported audio file formats.
- System displays file name and duration after successful upload.
- System shows a useful error if the file cannot be loaded.

### FR-3: Compare Recordings

The app shall compare the guru and disciple recordings when both files are available.

Acceptance criteria:

- Compare button is disabled until both files are loaded.
- Guru and disciple files may have different durations if each file is 5 minutes or shorter.
- Clicking Compare starts local analysis.
- App shows progress during analysis.
- App handles processing errors without crashing.
- App displays dual pitch graph after successful comparison.

### FR-4: Pitch Overlay Graph

The app shall show guru and disciple pitch contours on the same graph.

Acceptance criteria:

- Guru and disciple contours are visually distinct.
- Graph uses Hz on the Y-axis and seconds on the X-axis.
- Full pitch timeline for each recording is shown.
- Unvoiced or low-confidence sections do not create misleading lines.
- Leading silence, trailing silence, long endings, and non-vocal silent sections remain represented in pitch data.
- Graph remains readable for short and medium-length recordings.

### FR-5: Local Desktop Execution

The app shall run as a local desktop application.

Acceptance criteria:

- User can launch the app without running backend commands manually.
- The local FastAPI backend starts with or is managed by the desktop app.
- Core comparison works offline.
- App can be packaged as a desktop executable.

### FR-6: Local Backend API

The app shall keep core analysis behind a local FastAPI API.

Acceptance criteria:

- Desktop frontend calls the local backend API for comparison.
- API receives guru file and disciple file.
- API returns `guru_pitch_frames` and `disciple_pitch_frames`.
- API design can support a future React, Kotlin, or other frontend.

### FR-7: Handle Different Durations

The app shall accept recordings of different durations.

Acceptance criteria:

- Each uploaded file may be up to 5 minutes long.
- The two files do not need to have the same duration.
- Backend processes both full files and returns full pitch timelines.
- No phrase matching or alignment is required in MVP.

### FR-8: Specific Error Handling and Reset

The app shall handle invalid analysis scenarios with specific errors.

Acceptance criteria:

- No audio data returns a specific error.
- No vocals or no reliable vocal pitch returns a specific error.
- Errors are displayed as popups.
- After an error popup is dismissed, the UI resets to the starting state and the user starts again.

## 13. Non-Functional Requirements

### Performance

- Audio files up to 5 minutes should process within a reasonable time on a typical laptop.
- For MVP, target comparison completion within a reasonable time for recordings up to 5 minutes.

### Reliability

- The app should not crash when pitch detection fails.
- Errors should be shown clearly as popups.
- After an error popup is dismissed, the UI should reset to the starting state.
- The app should handle noisy recordings gracefully where possible.

### Privacy

- Audio files should not leave the local machine.
- Errors appear as popups and reset the UI after dismissal.
- The app should not store user recordings permanently.

### Usability

- The app should require minimal music-technology knowledge.
- Labels should use familiar musical language where possible.
- UI language shall be English for MVP.
- The UI should remain single-page and uncluttered.

### Maintainability

- Audio analysis should be implemented behind the FastAPI backend, separate from frontend UI code.
- Graph generation should be implemented as a separate component.
- Core analysis functions should be testable with sample audio files.
- The backend API contract should remain frontend-agnostic so future UI clients can reuse it.

## 14. Proposed System Architecture

### Repository Structure

The MVP should live in a single repository and run as one local desktop app. Inside that app, the frontend and backend should remain logically separated.

Recommended high-level structure:

- `backend/`: FastAPI API, audio loading, pitch extraction, compare service.
- `frontend/`: Python desktop UI, file picker, graph display, optional lightweight summary.
- `shared/`: shared schemas or constants if needed.
- `tests/`: backend unit tests and sample-analysis tests.
- `packaging/`: PyInstaller configuration.

### Backend Modules

1. FastAPI App Module
   - Exposes local API endpoints.
   - Accepts comparison requests from the desktop frontend.
   - Returns graph-ready data and statistics.

2. Audio Loader Module
   - Reads audio files using `librosa.load`, `soundfile`, and packaged FFmpeg support through `imageio-ffmpeg`.
   - Converts formats as needed for analysis.
   - Normalizes sample rate to `22050 Hz` and converts channels to mono.
   - Preserves full audio duration, including silence and long endings.
   - Performs basic validation.

3. Pitch Extractor Module
   - Extracts F0/pitch contour using `librosa.pyin`.
   - Filters low-confidence pitch values without deleting timeline regions.
   - Returns `PitchFrame` lists for guru and disciple.

4. Compare Service Module
   - Loads both files, runs pitch extraction, packages `ComparisonResult`.
   - Enforces minimum voiced content (`no_vocals_detected`).

### Frontend Modules

1. Single-Page Desktop UI Module
   - Handles file selection.
   - Shows selected file details.
   - Shows comparison status.

2. API Client Module
   - Calls the local FastAPI backend using `httpx`.
   - Sends guru file and disciple file.
   - Receives comparison result data.

3. Graph Module
   - Creates dual-contour graph from backend response using `pyqtgraph`.
   - Plots Hz vs `time_seconds` for each series.
   - Displays silent and unvoiced regions as gaps.

4. Summary Module (optional)
   - Displays durations and optional voiced fractions.

## 15. Suggested Data Model

### AudioFileInfo

- path
- file_name
- duration_seconds
- sample_rate
- channels
- format
- validation_status

### PitchFrame

- time_seconds
- frequency_hz
- confidence
- voiced
- silent_or_unvoiced

### ComparisonResult

- guru_file_info
- disciple_file_info
- guru_pitch_frames
- disciple_pitch_frames
- warnings (optional)

## 16. MVP Acceptance Criteria

The MVP is complete when:

- A user can open a local desktop app.
- The app shows one page with guru upload, disciple upload, compare, and graph area.
- The user can upload two valid audio files.
- The app extracts pitch from both files.
- The app shows a visual overlay comparing guru and disciple pitch (Hz vs time).
- The app preserves leading silence, trailing silence, long endings, and non-vocal silent sections in pitch data.
- The app provides graph visualization only (no match/higher/lower scoring in MVP).
- The app does not require Sa detection, swara labels, or phrase alignment for MVP completion.
- The Python desktop frontend calls a local FastAPI backend.
- The app runs locally without cloud processing.
- The app can be packaged into a desktop executable.

## 17. Risks and Challenges

### Pitch Detection Accuracy

Vocal recordings may include tanpura, harmonium, tabla, background noise, or room echo. These can reduce pitch detection accuracy.

Mitigation:

- Start with clean vocal recordings for MVP.
- Add clear recording guidance.
- Use confidence thresholds.
- Consider more robust pitch extraction libraries if needed.

### Different Keys and Timing

Guru and disciple may sing in different keys or at different speeds. MVP shows raw Hz overlays without normalization or DTW.

Mitigation:

- Document that visual comparison is shape-at-a-glance, not scored accuracy.
- Add Sa normalization and alignment in later versions if needed.
- Keep silence and long endings visible rather than trimming them.

### Musical Nuance

Hindustani classical music includes meend, andolan, gamak, kan swar, shruti nuance, and raga-specific expression. A simple pitch graph may not capture all musical correctness.

Mitigation:

- Keep MVP focused on pitch contour and statistical analysis.
- Expand later with phrase-specific and raga-aware analysis.

### Backend and Frontend Coupling

The MVP ships as one local app, but the backend should remain reusable by future frontends.

Mitigation:

- Keep core analysis behind FastAPI endpoints.
- Keep frontend-specific graph rendering outside the backend.
- Use explicit request and response schemas for comparison data.

## 18. To Be Done Later

### Restored Hindustani comparison features (removed from minimal MVP)

- Sa detection and cents-relative normalization across different keys (`guru_sa_hz`, `disciple_sa_hz`; error `sa_detection_failed`).
- Indian swara Y-axis labels and swara mapping (`S r R g G m M P d D n N`; `GET /swara-map`; per-frame `swara_label` / `swara_symbol`).
- Tolerance control (default 0, range 0–25, step 5) and `GET`/`PUT /settings/tolerance`; `tolerance_cents` on compare.
- Match/higher/lower/unknown frame classification using tolerance.
- Matched-portion discovery (sliding windows) and DTW alignment per `MatchedSegment`.
- Compare and graph **matched portions only**; `excluded_guru_ranges` / `excluded_disciple_ranges`; error `no_matching_pattern`.
- Concatenated `aligned_time` X-axis; `ComparisonFrame` and `aligned_frames` in API.
- Summary metrics: `overall_score` (`total_matching_intervals * 100 / total_intervals`), average deviation in cents, match/higher/lower/unknown percentages.
- Graph tolerance band and match/higher/lower region highlights.
- Highest deviation points in summary.
- Manual Sa selection.
- Manual correction of auto-detected Sa.
- Detailed rhythm, laya, taal, or early/late timing analysis.
- Raga-specific expected swara mapping.
- Playback of guru and disciple audio.
- Synced playback cursor on graph.
- Direct microphone recording.
- Live real-time singing feedback.
- Beginner-friendly coaching feedback or practice suggestions.
- Section-by-section feedback.
- Export graph as image or PDF.
- Export statistical report.
- Save comparison sessions.
- Compare against multiple guru takes.
- Support for tabla/taal timing analysis.
- Support for instrumental recordings.
- AI-generated practice recommendations.
- Multi-language UI, such as English, Hindi, and Marathi.
- React frontend using the same FastAPI backend.
- Kotlin frontend using the same FastAPI backend.

## 19. Resolved Product Decisions

1. MVP extracts and overlays pitch contours (Hz vs time).
2. Guru and disciple may have different durations; both full timelines are returned.
3. Sa detection, swara mapping, DTW, and tolerance scoring are deferred.
4. Exercise type does not change MVP analysis (F0 extraction only).
5. Maximum recording length for MVP is 5 minutes per file.
6. Windows is the first target operating system.
7. Graph Y-axis is Hz (linear); X-axis is wall-clock seconds.
8. MVP uses file upload only.
9. MVP does not include real-time recording, playback, or coaching text.
10. MVP UI language is English.
11. Backend and frontend live in the same repository for MVP.
12. Backend is a Python FastAPI API so future frontends can reuse it.
13. MVP uses Python `3.11.x`, `librosa`, `librosa.pyin`, `PySide6`, `pyqtgraph`, `PyInstaller`.
14. WAV, MP3, and M4A; static backend port 8765; Clear required; client-side pre-validation; `no_vocals_detected` only.
15. pyin thresholds are defined in `07-architecture.md`.

## 20. Resolved Clarifications (MVP)

1. No tolerance UI or compare parameter in MVP.
2. No overall match score or match/higher/lower percentages in MVP.
3. Graph shows full-timeline dual F0 contours, not matched-only segments.
4. Highest deviation points, swara bins, and Sa histogram are out of scope.

## 21. Current Assumptions

- The MVP is for vocal Hindustani classical music practice (visual pitch overlay).
- The first version is a local Windows desktop application.
- Python `3.11.x` is the primary runtime.
- The backend is a local FastAPI API; the frontend is `PySide6` + `pyqtgraph`.
- The app processes uploaded files only in the first version.
- The core audio-analysis engine is `librosa`; graphing is `pyqtgraph`.
- The app works offline with a simple single-page UI.
