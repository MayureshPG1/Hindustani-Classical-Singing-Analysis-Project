# Product Requirements Document: Hindustani Classical Music Learning App

## 1. Product Summary

The product is a local desktop application for Hindustani classical music learning. It allows a guru to upload a recorded audio file and a disciple to upload their own recorded version of the same musical phrase, exercise, bandish segment, raga phrase, taan, alap, or swara practice. The app compares both recordings and presents a graphical analysis that helps the disciple understand where their pitch contour matches, goes higher, or goes lower than the guru's reference performance.

The first version will be a single-page desktop app with three core actions:

1. Upload guru audio.
2. Upload disciple audio.
3. Compare and view graphical analysis.

The app should primarily use Python for the backend/audio-analysis logic and should run locally as a compiled desktop application. No cloud upload should be required for the MVP. The first implementation will keep the backend API and frontend app in the same repository as one local app, but the backend should be designed as a FastAPI service so a future React, Kotlin, or other frontend can reuse the same analysis API.

## 2. Problem Statement

In Hindustani classical music training, disciples often learn by listening to a guru and attempting to reproduce phrases accurately. Feedback usually depends on live correction from the guru. When practicing alone, disciples do not have an easy way to see whether their pitch movement, note placement, and melodic shape match the guru's reference.

The app solves this by comparing two recorded audio files and creating a visual overlay of the guru's voice and the disciple's voice. The disciple can see:

- Where their pitch matches the guru.
- Where they sing higher than the guru.
- Where they sing lower than the guru.
- How close the overall melodic contour is to the guru's version.

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

## 6. Core User Flow

1. User opens the desktop app.
2. User clicks "Upload Guru Voice" and selects an audio file.
3. App validates the file and displays basic file information.
4. User clicks "Upload Disciple Voice" and selects an audio file.
5. App validates the file and displays basic file information.
6. User reviews or edits the tolerance value. The default tolerance is 50 cents.
7. User clicks "Compare".
8. App processes both audio files locally.
9. App normalizes guru and disciple pitch contours relative to their detected Sa values.
10. App displays an overlay graph comparing guru pitch and disciple pitch.
11. App highlights matching areas, higher-than-guru areas, and lower-than-guru areas based on the tolerance value.
12. User can inspect the graph and summary metrics.

## 7. MVP User Interface Requirements

The MVP is a single-page desktop UI.

### Required Controls

- Button: "Upload Guru Voice"
- Button: "Upload Disciple Voice"
- Editable numeric field: "Tolerance", default value 50
- Button/control: decrease tolerance
- Button/control: increase tolerance
- Button: "Compare"
- Optional button: "Clear"

### Tolerance Control

The front page shall include an editable tolerance field named "Tolerance". The tolerance value represents the allowed pitch difference in cents for classifying guru and disciple pitch as matching.

Requirements:

- Default value: 50 cents.
- User can type a numeric value directly.
- User can increase or decrease the value using plus and minus buttons next to the field.
- Plus and minus controls change the value by 10 cents per click.
- The comparison graph and statistics shall use the current tolerance value.
- Lower tolerance makes the comparison stricter.
- Higher tolerance makes the comparison more forgiving.

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
  - Aligning recordings
  - Generating graph
  - Complete
  - Error

- Comparison graph:
  - Guru pitch contour
  - Disciple pitch contour
  - Match zones
  - Higher/lower deviation zones
  - Timeline

- Summary panel:
  - Overall match score
  - Average pitch deviation
  - Percentage of matched sections
  - Highest deviation points
  - Percentage of higher-than-guru sections
  - Percentage of lower-than-guru sections

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
- M4A, if local decoding support is stable in the chosen packaging setup

### File Constraints

Initial assumptions:

- Maximum audio length: 2 minutes per file for MVP.
- Recommended recording length: 10 seconds to 2 minutes.
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
- No sufficiently similar pitch-contour pattern between guru and disciple recordings.

Guru and disciple clips may have different durations as long as each file is 2 minutes or shorter. Different durations should not block comparison by themselves.

## 9. Audio Analysis Requirements

The comparison should focus primarily on vocal pitch contour. Timing alignment may be used internally to align two pitch contours, but the MVP shall not provide detailed rhythm, taal, or timing feedback.

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
- Bundle FFmpeg support through `imageio-ffmpeg` so MP3/M4A decoding is more reliable in the packaged Windows app.
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

### 9.3 Sa and Relative Pitch

Hindustani classical music is based on relative pitch around the tonic, commonly Sa. The app shall compare pitch relative to Sa rather than using absolute frequency matching.

MVP behavior:

1. Auto-detect Sa for the guru recording.
2. Auto-detect Sa for the disciple recording.
3. Normalize both pitch contours relative to their own detected Sa.
4. Compare the normalized relative pitch contours.

Required behavior:

- Guru and disciple may sing in different scales.
- The MVP shall support different pitch scales by normalizing both recordings to Sa.
- Absolute pitch matching is not part of the MVP comparison.
- Manual Sa correction can be added later if auto-detection is not sufficient.

Implementation library decision:

- Use `librosa`, `numpy`, and `scipy` to implement Sa detection.
- The MVP shall not depend on a specialized Hindustani music package for Sa detection.
- Recommended approach: extract F0, remove low-confidence/unvoiced frames from the Sa estimation step only, build a weighted pitch-class or cents histogram, identify the strongest stable pitch region, and use that as detected Sa.
- The original graph timeline must still preserve unvoiced and silent frames even if they are excluded from Sa estimation.

### 9.4 Pitch Representation

The app should convert raw frequency into a musically meaningful representation:

- Frequency in Hz for internal analysis.
- Cents relative to Sa for comparison.
- Indian swara labels for graph display, using full labels such as Sa, Re, Ga, Ma and compact symbols where the graph needs shorter labels.

Example:

- If guru and disciple sing the same phrase in different absolute keys, comparison should still work because both recordings are normalized relative to their own Sa.
- The graph should help the user compare melodic shape and swara-relative pitch accuracy, not absolute vocal register.

### 9.4.1 Swara Label Mapping

The MVP shall show komal and tivra swaras. The graph should use Indian swara labels, with the following mapping available to the frontend and backend:

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

The graph should prefer readable labels like Sa, Re, Ga, and Ma where space allows. Compact symbols may be used for dense axis ticks, hover values, or data payloads, but they must follow the mapping above.

### 9.5 Time Alignment

The guru and disciple recordings may not have identical timing. The app may align the two pitch contours before calculating pitch differences, but the MVP should use this only to support pitch comparison.

Recommended approach:

- Use `librosa.sequence.dtw` for dynamic time warping on pitch contour features.
- Align similar melodic shapes even if the disciple sings slower or faster.
- Find similar pitch-contour portions even when guru and disciple files have different durations.
- Compare only matched similar portions.
- Leave non-similar additional portions from either uploaded audio out of comparison and scoring.
- Return a specific error if no sufficiently similar vocal pattern can be found.
- Preserve the full original timeline and do not remove silence or endings.
- Do not present detailed early/late rhythm feedback in the MVP.

### 9.6 Difference Calculation

For each aligned time frame, the app should calculate:

- Guru pitch.
- Disciple pitch.
- Difference in cents.
- Whether the disciple is higher, lower, or within acceptable range.

Tolerance behavior:

- Match: absolute pitch difference is less than or equal to the current tolerance value.
- Higher: disciple pitch is more than the tolerance value above the guru pitch.
- Lower: disciple pitch is more than the tolerance value below the guru pitch.
- Default tolerance: 50 cents.
- Tolerance step size: 10 cents.

The tolerance value shall come from the front-page Tolerance field and shall be editable before each comparison.

Implementation library decision:

- Use `numpy` for cents-difference calculation, tolerance classification, percentages, and summary scores.
- Keep scoring as custom app logic because match/higher/lower classification is specific to this product.

### 9.7 Audio Analysis Library Plan

The best overall Python library for the app's audio-analysis backend is `librosa`. It covers most of the MVP audio tasks: loading, mono conversion, resampling, F0 extraction, frequency conversion helpers, and DTW alignment. It does not cover the desktop UI or polished graph rendering, so the graph/UI layer shall use `PySide6` and `pyqtgraph`.

There is no single Python package that covers the complete product: Hindustani Sa-relative comparison, custom swara mapping, local API boundary, desktop UI, and graph rendering. The MVP should therefore use `librosa` as the core DSP engine and implement the domain-specific Sa detection, swara mapping, tolerance classification, and scoring as custom backend logic.

| PRD Task | Final Library Choice | Justification |
| --- | --- | --- |
| Load audio | `librosa.load`, `soundfile`, `imageio-ffmpeg` | `librosa.load` loads files into NumPy arrays, can convert to mono, and can resample. `soundfile` is the primary audio backend. `imageio-ffmpeg` helps package FFmpeg decoding support for MP3/M4A on Windows. |
| Preserve silence and endings | Custom logic with `numpy` arrays | The product explicitly must not trim endings or silent/non-vocal sections, so the backend should avoid silence-trimming helpers and preserve the full timeline. |
| Mono conversion | `librosa.load(..., mono=True)` or `librosa.to_mono` | Built-in support, simple, and consistent with the rest of the audio pipeline. |
| Resampling | `librosa.load(..., sr=22050)` with `soxr` | Keeps analysis predictable across file formats and sample rates. `librosa` uses high-quality `soxr` resampling. |
| Pitch/F0 extraction | `librosa.pyin` | Provides F0, voiced/unvoiced decisions, and voiced probability for monophonic vocal pitch tracking. |
| Backup pitch extractor | Later-scope `torchcrepe` evaluation | CREPE-style neural pitch tracking may be more robust in some conditions, but it adds PyTorch size and packaging complexity. |
| Sa detection | Custom algorithm using `librosa`, `numpy`, and `scipy` | No general-purpose library perfectly solves Hindustani Sa detection for this MVP. Sa detection should use extracted F0 and stable-pitch histogram logic. |
| Swara mapping | Custom table | The app's `S r R g G m M P d D n N` mapping is domain-specific and should remain explicit app logic. |
| Alignment | `librosa.sequence.dtw` | DTW is already available in `librosa` and fits guru/disciple pitch contour alignment. |
| Difference and scoring | `numpy` | Cents difference, tolerance classification, percentages, and score calculation are straightforward vector operations. |
| Graph display | `pyqtgraph` | Fast, native Qt plotting that works with `PySide6` and NumPy; better suited than Matplotlib for an interactive desktop overlay graph. |

Recommended audio-comparison pipeline:

1. Decode input audio to PCM.
2. Load full audio without trimming.
3. Convert to mono.
4. Resample to `22050 Hz`.
5. Run `librosa.pyin` with a human vocal pitch range, initially `fmin=50 Hz` and `fmax=1000 Hz`.
6. Keep the full timeline and represent unvoiced/silent frames as masked values or `NaN`.
7. Auto-detect Sa separately for guru and disciple.
8. Convert both F0 contours to cents relative to their own Sa.
9. Map cents to swara labels using `S r R g G m M P d D n N`.
10. Align contours with DTW where useful.
11. Compute disciple-minus-guru cents difference.
12. Classify each aligned frame using the selected tolerance.
13. Return graph-ready JSON to the frontend.
14. Render guru line, disciple line, tolerance band, and match/high/low regions in `pyqtgraph`.

## 10. Graphical Analysis Requirements

The graph is the primary output of the app.

### Required Graph Elements

- X-axis: Time or aligned phrase progression, while preserving visible silent/unvoiced regions.
- Y-axis: Indian swara labels, backed internally by cents relative to Sa.
- Swara labels include komal and tivra swaras using the defined mapping.
- Guru line: one clear color.
- Disciple line: second clear color.
- Match zones: neutral or green highlight.
- Disciple higher than guru: highlighted above the guru contour.
- Disciple lower than guru: highlighted below the guru contour.
- Gaps or unvoiced areas: visible breaks or muted segments.
- Tolerance band around the guru contour based on the current tolerance value.
- Graph and statistics should focus on matched similar portions only.
- Non-similar additional portions should be left out of the comparison graph and metrics.

### Optional Graph Elements

- Hover tooltip showing:
  - Time
  - Guru pitch
  - Disciple pitch
  - Difference in cents
  - Higher, lower, or match

- Zoom and pan.
- Markers for major deviation points.

### Summary Metrics

The app should calculate and display:

- Overall match score from 0 to 100.
- Average absolute pitch deviation in cents.
- Percentage of frames within match threshold.
- Percentage of frames where disciple is higher.
- Percentage of frames where disciple is lower.
- Tolerance value used for the comparison.
- Non-similar additional portions excluded from scoring.

## 11. Desktop App Requirements

### Recommended Architecture

The app should use a local API-based desktop architecture:

- Python FastAPI backend for audio upload, validation, analysis, and comparison.
- Python desktop frontend app for file selection, tolerance input, graph display, and statistics.
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
10. `numpy` and `scipy` for numerical processing, Sa detection, scoring, and smoothing/filtering operations.
11. `soundfile` for audio file reading support used by `librosa`.
12. `soxr` for high-quality resampling through `librosa`.
13. `imageio-ffmpeg` to package FFmpeg support for MP3/M4A decoding on Windows.
14. `PyInstaller` for compiling into a local Windows desktop executable.

Recommended MVP choice:

- Use `librosa` as the main DSP engine rather than mixing multiple pitch/audio-analysis libraries in MVP.
- Use custom backend logic for Sa detection, swara mapping, tolerance classification, and scoring.
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
- Compare request with guru file, disciple file, and tolerance value.
- Compare response containing aligned graph data, swara-relative pitch values, classifications, and summary statistics.
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
- The current tolerance value is sent with the comparison request.
- Guru and disciple files may have different durations if each file is 2 minutes or shorter.
- Clicking Compare starts local analysis.
- App shows progress during analysis.
- App handles processing errors without crashing.
- App displays graph and summary after successful comparison.

### FR-4: Set Comparison Tolerance

The app shall allow the user to set the pitch tolerance used for matching guru and disciple pitch contours.

Acceptance criteria:

- Tolerance field is visible on the single-page UI.
- Default tolerance is 50 cents.
- User can edit tolerance manually.
- User can increase or decrease tolerance using plus and minus controls.
- Plus and minus controls change tolerance by 10 cents per click.
- Compare uses the currently displayed tolerance value.
- The result displays the tolerance value used for analysis.

### FR-5: Pitch Overlay Graph

The app shall show guru and disciple pitch contours on the same graph.

Acceptance criteria:

- Guru and disciple contours are visually distinct.
- Graph uses Indian swara labels on the pitch axis.
- Graph supports komal and tivra swara labels using the defined mapping.
- Graph compares normalized pitch relative to each singer's detected Sa.
- Graph compares only matched similar portions when files contain extra non-similar material.
- Matching, higher, and lower areas are clearly indicated.
- Matching, higher, and lower classifications use the current tolerance value.
- Unvoiced or low-confidence sections do not create misleading lines.
- Leading silence, trailing silence, long endings, and non-vocal silent sections remain visible in the graph timeline.
- Graph remains readable for short and medium-length recordings.

### FR-6: Summary Analysis

The app shall show simple numerical analysis after comparison.

Acceptance criteria:

- Overall match score is visible.
- Average deviation is visible.
- Higher/lower/matching percentages are visible.
- Tolerance used for comparison is visible.
- Metrics exclude non-similar additional portions left out of comparison.
- Scores are explained using plain labels, not technical jargon only.
- The MVP does not generate coaching advice or qualitative practice feedback.

### FR-7: Local Desktop Execution

The app shall run as a local desktop application.

Acceptance criteria:

- User can launch the app without running backend commands manually.
- The local FastAPI backend starts with or is managed by the desktop app.
- Core comparison works offline.
- App can be packaged as a desktop executable.

### FR-8: Local Backend API

The app shall keep core analysis behind a local FastAPI API.

Acceptance criteria:

- Desktop frontend calls the local backend API for comparison.
- API receives guru file, disciple file, and tolerance value.
- API returns graph-ready pitch data and summary statistics.
- API design can support a future React, Kotlin, or other frontend.

### FR-9: Handle Different Durations and Extra Material

The app shall compare recordings of different durations when they contain similar pitch-contour portions.

Acceptance criteria:

- Each uploaded file may be up to 2 minutes long.
- The two files do not need to have the same duration.
- Backend processes both full files.
- Backend finds similar portions between guru and disciple recordings.
- Backend compares only matched similar portions.
- Non-similar additional portions from either file are left out of comparison and scoring.
- If no sufficiently similar pattern is found, the backend returns a specific error.

### FR-10: Specific Error Handling and Reset

The app shall handle invalid analysis scenarios with specific errors.

Acceptance criteria:

- No audio data returns a specific error.
- No vocals or no reliable vocal pitch returns a specific error.
- Sa detection failure returns a specific error.
- No matching pattern returns a specific error.
- Errors are displayed as popups.
- After an error popup is dismissed, the UI resets to the starting state and the user starts again.

## 13. Non-Functional Requirements

### Performance

- Audio files up to 2 minutes should process within a reasonable time on a typical laptop.
- For MVP, target comparison completion within 30 seconds for recordings under 2 minutes.

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

- `backend/`: FastAPI API, audio loading, pitch extraction, Sa detection, comparison, and scoring.
- `frontend/`: Python desktop UI, file picker, tolerance control, graph display, and summary statistics.
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

3. Sa Detection Module
   - Auto-detects Sa for guru recording using `librosa`, `numpy`, and `scipy`.
   - Auto-detects Sa for disciple recording using the same algorithm.
   - Reports detection confidence where possible.

4. Pitch Analysis Module
   - Extracts F0/pitch contour using `librosa.pyin`.
   - Filters low-confidence pitch values without deleting timeline regions.
   - Converts pitch to cents relative to each recording's detected Sa.
   - Maps relative pitch regions to Indian swara labels for graph display.

5. Alignment Module
   - Optionally aligns guru and disciple contours using `librosa.sequence.dtw`.
   - Finds similar pitch-contour portions across different-duration recordings.
   - Leaves non-similar additional portions out of comparison and scoring.
   - Supports pitch comparison when performances are slower or faster.
   - Does not remove silence or endings from the source timeline.

6. Scoring Module
   - Uses the user-selected tolerance value.
   - Calculates deviation metrics using `numpy`.
   - Calculates match, higher, and lower percentages.
   - Calculates overall score.

### Frontend Modules

1. Single-Page Desktop UI Module
   - Handles file selection.
   - Shows selected file details.
   - Shows tolerance input with plus and minus controls.
   - Shows comparison status.

2. API Client Module
   - Calls the local FastAPI backend using `httpx`.
   - Sends guru file, disciple file, and tolerance value.
   - Receives comparison result data.

3. Graph Module
   - Creates overlay graph from backend response using `pyqtgraph`.
   - Displays Indian swara labels.
   - Adds match/higher/lower visual regions.
   - Displays silent and unvoiced regions without hiding them.

4. Summary Module
   - Displays statistical analysis.
   - Shows overall score, average deviation, match percentage, higher percentage, lower percentage, and tolerance used.

## 15. Suggested Data Model

### AudioFileInfo

- path
- file_name
- duration_seconds
- sample_rate
- channels
- format
- validation_status

### ToleranceSettings

- tolerance_cents
- default_tolerance_cents: 50
- minimum_tolerance_cents
- maximum_tolerance_cents
- step_cents: 10

### PitchFrame

- time_seconds
- frequency_hz
- confidence
- cents_from_sa
- swara_label
- voiced
- silent_or_unvoiced

### ComparisonFrame

- aligned_time
- original_guru_time
- original_disciple_time
- guru_cents_from_sa
- disciple_cents_from_sa
- guru_swara_label
- disciple_swara_label
- difference_cents
- classification: match, higher, lower, unknown

### ComparisonResult

- guru_file_info
- disciple_file_info
- guru_sa_hz
- disciple_sa_hz
- tolerance_cents
- aligned_frames
- average_deviation_cents
- match_percentage
- higher_percentage
- lower_percentage
- overall_score

## 16. MVP Acceptance Criteria

The MVP is complete when:

- A user can open a local desktop app.
- The app shows one page with guru upload, disciple upload, compare, and graph area.
- The page includes a Tolerance field with default value 50 and plus/minus controls that change the value by 10 cents.
- The user can upload two valid audio files.
- The app extracts pitch from both files.
- The app auto-detects Sa for both files.
- The app compares pitch relative to each recording's detected Sa.
- The app aligns the pitch contours if needed for comparison.
- The app handles different-duration clips by finding similar portions.
- The app excludes non-similar additional portions from comparison and scoring.
- The app shows a visual overlay comparing guru and disciple pitch.
- The graph uses Indian swara labels.
- The graph shows komal and tivra swaras using the defined swara mapping.
- The app clearly shows higher, lower, and matching sections.
- The app preserves leading silence, trailing silence, long endings, and non-vocal silent sections in the analysis timeline.
- The app shows basic summary metrics.
- The app provides statistical analysis only, without coaching feedback.
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

### Sa Detection

Accurate comparison in Hindustani music depends on identifying the correct Sa for both guru and disciple recordings.

Mitigation:

- Auto-detect Sa separately for guru and disciple recordings.
- Normalize both pitch contours relative to detected Sa before comparison.
- Add manual Sa selection later if auto-detection is not reliable enough.

### Timing Differences

Guru and disciple may sing at different speeds, making direct pitch contour comparison misleading.

Mitigation:

- Use dynamic time warping or a similar alignment approach only to support pitch comparison.
- Do not show detailed rhythm, taal, or early/late timing analysis in the MVP.
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

- Manual Sa selection.
- Manual correction of auto-detected Sa.
- Absolute pitch comparison mode.
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

1. MVP compares pitch primarily.
2. Guru and disciple may sing in different pitch scales.
3. The app normalizes both recordings relative to detected Sa before comparison.
4. Sa is auto-detected first.
5. Exercise type does not affect MVP analysis because the app is doing frequency and pitch-contour analysis.
6. Maximum recording length for MVP is 2 minutes per file.
7. Windows is the first target operating system.
8. Graph uses Indian swara labels.
9. MVP uses file upload only.
10. MVP does not include real-time recording or real-time playback.
11. MVP does not include audio playback of uploaded files.
12. MVP UI language is English.
13. MVP provides graph comparison and statistical analysis only, not coaching feedback.
14. Export is later scope.
15. Backend and frontend live in the same repository for MVP.
16. Backend is a Python FastAPI API so future React or Kotlin frontends can reuse it.
17. Tolerance plus/minus step size is 10 cents.
18. Swara labels use full Indian names such as Sa, Re, Ga, and Ma.
19. MVP includes komal and tivra swara labels using the defined symbol mapping.
20. MVP uses Python `3.11.x`.
21. MVP uses `librosa` as the main audio-analysis/DSP library.
22. MVP uses `librosa.pyin` for pitch extraction.
23. MVP uses `librosa.sequence.dtw` for optional pitch-contour alignment.
24. MVP uses `PySide6` for the desktop frontend.
25. MVP uses `pyqtgraph` for graph rendering.
26. MVP uses `PyInstaller` for Windows packaging.
27. MVP does not include `praat-parselmouth`, `pyworld`, `Essentia`, `CREPE`, or `torchcrepe` as default dependencies.

## 20. Remaining Clarifying Questions

1. What should be the minimum and maximum allowed values for the Tolerance field?

## 21. Current Assumptions

- The MVP is for vocal Hindustani classical music.
- The first version is a local Windows desktop application.
- Python `3.11.x` is the primary backend, frontend, and analysis runtime for MVP.
- The backend is a local FastAPI API.
- The frontend is a Python desktop app built with `PySide6`.
- The app will process uploaded files, not live microphone input, in the first version.
- The first useful analysis will be relative pitch contour comparison.
- The core audio-analysis engine is `librosa`.
- The graphing engine is `pyqtgraph`.
- The packaging tool is `PyInstaller`.
- Graphical output and statistical analysis are more important than textual coaching in the first version.
- The app should work offline.
- The user wants a simple single-page UI.
