# Functional Spec

## Scope

The MVP is a single-page Windows desktop app for local comparison of two uploaded vocal recordings. It extracts F0 from each file and displays guru and disciple pitch contours on one graph (Hz vs wall-clock time). There is no Sa detection, swara mapping, phrase matching, DTW alignment, or match/higher/lower scoring in MVP.

## Functional Requirements

### FS-1: Launch Local Desktop App

The app shall launch as a Windows desktop application.

Acceptance criteria:

- User can open the app without manually starting a backend.
- The local FastAPI backend starts with or is managed by the desktop app.
- Backend binds only to localhost.
- App opens to the single comparison page.

### FS-2: Upload Guru Audio

The app shall allow the user to select a guru audio file.

Acceptance criteria:

- `Upload Guru Voice` opens a local file picker.
- Supported files can be selected.
- File name, duration, format, and validation state are shown.
- Invalid files produce a clear error popup and reset the UI after dismissal.

### FS-3: Upload Disciple Audio

The app shall allow the user to select a disciple audio file.

Acceptance criteria:

- `Upload Disciple Voice` opens a local file picker.
- Supported files can be selected.
- File name, duration, format, and validation state are shown.
- Invalid files produce a clear error popup and reset the UI after dismissal.

### FS-4: Validate Audio Files (Inspect)

The app shall validate uploaded files via `POST /audio/inspect` before comparison.

Validation rules:

- File must be readable.
- File type must be supported.
- Duration must be less than or equal to 5 minutes.
- File must contain audio data.
- Audio must contain at least some detectable vocal pitch (`no_vocals_detected` if not).

Inspect response:

- `file_info`: `AudioFileInfo`.
- `pitch_metadata`: full-file voiced stats (`voiced_frame_count`, `total_frame_count`, `voiced_fraction`).

Supported MVP formats:

- WAV
- MP3
- M4A

The frontend shall perform basic client-side validation before calling the API (extension whitelist, file exists, size > 0, duration ≤ 300 s when metadata is available locally).

### FS-5: Compare Recordings

The app shall compare guru and disciple recordings using local processing.

Acceptance criteria:

- Compare button is disabled until both files are valid.
- Clicking Compare sends both files to the local backend (no tolerance parameter).
- App shows progress states.
- Backend returns pitch frame arrays for both recordings.
- App displays dual-contour graph.
- Errors do not crash the app.
- Errors are shown as popups.
- After an error popup is dismissed, the UI resets to the starting state.

### FS-6: Preserve Full Timeline

The app shall preserve the full uploaded audio timeline in pitch extraction.

Acceptance criteria:

- No leading silence trimming.
- No trailing silence trimming.
- No long-ending trimming.
- No removal of non-vocal silent sections from the frame list.
- Silent and unvoiced regions are represented as gaps or unplotted F0.

### FS-7: Extract Pitch

The backend shall extract F0/pitch over time.

Acceptance criteria:

- Use `librosa.pyin`.
- Return F0, voiced/unvoiced state, voiced probability or confidence, and frame time.
- Low-confidence pitch frames are not plotted as reliable pitch.
- Unvoiced frames remain present in the timeline.

### FS-8: Handle No Audio and No Vocals

The backend shall detect common invalid analysis scenarios and return specific errors.

Required error cases:

- No audio data or empty decoded waveform: `no_audio_detected`.
- No vocal/pitch content detected: `no_vocals_detected` only.
- Unexpected comparison failure: `comparison_failed`.

Acceptance criteria:

- Each case returns a structured API error.
- Frontend displays the error in a popup.
- After the popup is dismissed, the UI resets to the starting state.
- User must upload files again to retry.

### FS-9: Show Graph

The frontend shall render a dual pitch-contour graph.

Acceptance criteria:

- Guru and disciple contours are visually distinct.
- Y-axis: frequency in Hz (linear).
- X-axis: `time_seconds` (wall-clock, full timeline per recording).
- Both full pitch timelines are shown (not matched-only subsets).
- Unvoiced or low-confidence sections do not create misleading lines.
- Hover tooltips and zoom/pan are deferred (not required for MVP).

### FS-10: Show Basic File Summary (Optional)

The frontend may show lightweight readouts after comparison (not scoring).

Examples:

- Guru and disciple duration.
- Voiced frame count or voiced fraction per file.

Match/higher/lower percentages and overall score are out of scope for MVP.

### FS-11: Clear Session and Temporary Files

The app shall provide a Clear control and clean up session data.

Acceptance criteria:

- Clear button is visible on the single-page UI.
- Clear calls `POST /api/v1/session/clear`, resets UI, and deletes all temporary session files.
- Error popup dismissal performs the same reset and temp-file deletion.

### FS-12: Do Not Provide Coaching Feedback

The MVP shall not generate qualitative coaching advice.

The MVP shows pitch overlay only, not interpretive practice feedback.

## Out of scope for MVP (to be added later)

Not required for minimal MVP; implement when product scope expands:

| Area | Deferred capability |
| --- | --- |
| Sa | Auto-detect Sa per recording; `guru_sa_hz` / `disciple_sa_hz`; `sa_detection_failed` |
| Swaras | Map pitch to `S r R g G m M P d D n N`; swara Y-axis; `GET /swara-map`; `cents_from_sa` on frames |
| Tolerance | UI control 0–25 cents (step 5); `GET`/`PUT /settings/tolerance`; `tolerance_cents` on compare; `invalid_tolerance` |
| Matching | Find similar portions; exclude non-similar material; `no_matching_pattern` |
| Alignment | DTW inside `MatchedSegment`; `aligned_frames`; concatenated `aligned_time` graph axis |
| Scoring | Classify match/higher/lower/unknown; `ComparisonMetrics`; tolerance band and highlights on graph |
| API fields | `matched_segments`, `excluded_guru_ranges`, `excluded_disciple_ranges`, `metrics` |
| UX | Processing states: detecting Sa, finding portions, aligning, calculating comparison |
| Metrics | `overall_score`, deviation and match/higher/lower percentages; highest deviation points |
