# Functional Spec

## Scope

The MVP is a single-page Windows desktop app for local comparison of two uploaded vocal recordings. It compares relative pitch contours after auto-detecting Sa for each recording.

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

### FS-4: Validate Audio Files

The app shall validate uploaded files before comparison.

Validation rules:

- File must be readable.
- File type must be supported.
- Duration must be less than or equal to 2 minutes.
- File must contain audio data.
- Audio must contain at least some detectable vocal pitch.

Supported MVP formats:

- WAV
- MP3

The frontend shall perform basic client-side validation before calling the API (extension whitelist, file exists, size > 0, duration ≤ 120 s when metadata is available locally).

### FS-5: Configure Tolerance

The app shall provide a `Tolerance` numeric field.

Acceptance criteria:

- Default tolerance is 0 cents.
- Valid range is 0 to 25 cents inclusive.
- User can type a numeric tolerance value.
- Plus button increases tolerance by 5 cents.
- Minus button decreases tolerance by 5 cents.
- Compare uses the currently displayed tolerance value.
- Result displays the tolerance used.
- Values outside 0–25 return `invalid_tolerance`.

### FS-6: Compare Recordings

The app shall compare guru and disciple recordings using local processing.

Acceptance criteria:

- Compare button is disabled until both files are valid.
- Clicking Compare sends both files and tolerance to the local backend.
- App shows progress states.
- Backend returns graph-ready comparison data.
- App displays graph and statistics.
- Errors do not crash the app.
- Errors are shown as popups.
- After an error popup is dismissed, the UI resets to the starting state.

### FS-7: Preserve Full Timeline

The app shall preserve the full uploaded audio timeline.

Acceptance criteria:

- No leading silence trimming.
- No trailing silence trimming.
- No long-ending trimming.
- No removal of non-vocal silent sections.
- Silent and unvoiced regions are represented as gaps, muted regions, or unknown frames.

### FS-8: Extract Pitch

The backend shall extract F0/pitch over time.

Acceptance criteria:

- Use `librosa.pyin`.
- Return F0, voiced/unvoiced state, voiced probability or confidence, and frame time.
- Low-confidence pitch frames are not plotted as reliable pitch.
- Unvoiced frames remain present in the timeline.

### FS-9: Auto-Detect Sa

The backend shall auto-detect Sa separately for guru and disciple.

Acceptance criteria:

- Sa is detected from each recording's pitch data.
- Guru and disciple may have different absolute pitch scales.
- Comparison uses cents relative to each recording's detected Sa.
- API returns detected `guru_sa_hz` and `disciple_sa_hz`.

### FS-10: Map Swaras

The backend shall map relative pitch regions to Indian swara labels.

Acceptance criteria:

- Mapping includes komal and tivra swaras.
- Supported symbols: `S r R g G m M P d D n N`.
- Frontend can display readable labels such as Sa, Komal Re, and Tivra Ma.

### FS-11: Align Pitch Contours

The backend shall align pitch contours only within matched similar portions.

Acceptance criteria:

- Use `librosa.sequence.dtw` inside each `MatchedSegment` only (not on full-file contours).
- Alignment supports slower/faster singing within a matched segment.
- Alignment is used only for pitch comparison.
- MVP does not show detailed rhythm, taal, or early/late feedback.
- Matched-portion discovery uses sliding-window correlation/DTW thresholds defined in [`07-architecture.md`](07-architecture.md).

### FS-12: Match Similar Portions Across Different Durations

The backend shall handle recordings of different durations, as long as each file is 2 minutes or shorter.

Acceptance criteria:

- Guru and disciple files may have different durations.
- Backend processes both full uploaded files.
- Backend finds similar pitch-contour portions between the two recordings.
- Backend compares only matched similar portions.
- Non-similar additional portions from either recording are left out of comparison and scoring.
- Full source pitch timelines may still be retained for debugging and internal analysis.
- If no sufficiently similar vocal pattern can be found, backend returns a specific `no_matching_pattern` error.

### FS-13: Classify Comparison Frames

The backend shall classify each comparable frame.

Classification:

- `match`: absolute pitch difference is less than or equal to tolerance.
- `higher`: disciple pitch is more than tolerance above guru pitch.
- `lower`: disciple pitch is more than tolerance below guru pitch.
- `unknown`: frame cannot be reliably compared.

### FS-14: Handle No Audio, No Vocals, and No Match Cases

The backend shall detect common invalid analysis scenarios and return specific errors.

Required error cases:

- No audio data or empty decoded waveform: `no_audio_detected`.
- No vocal/pitch content detected: `no_vocals_detected` only.
- Sa cannot be detected reliably: `sa_detection_failed`.
- No similar matching pattern exists between guru and disciple recordings: `no_matching_pattern`.
- Unexpected comparison failure: `comparison_failed`.

Acceptance criteria:

- Each case returns a structured API error.
- Frontend displays the error in a popup.
- After the popup is dismissed, the UI resets to the starting state.
- User must upload files again to retry.

### FS-15: Show Graph

The frontend shall render a graphical overlay for matched portions only.

Acceptance criteria:

- Guru and disciple contours are visually distinct.
- Y-axis uses Indian swara labels (fixed 100-cent swara bins; shruti microtones out of scope).
- X-axis uses concatenated `aligned_time` across matched segments (0…N−1), not full-upload wall-clock time.
- Graph displays matched similar portions only (no full-timeline overlay).
- Graph includes tolerance band around guru contour on matched frames.
- Graph shows match, higher, and lower sections.
- Silent/unvoiced regions within matched segments do not create misleading lines.
- Hover tooltips and zoom/pan are deferred (not required for MVP).

### FS-16: Show Statistics

The frontend shall show statistical analysis.

Required metrics:

- Overall score from 0 to 100: `total_matching_intervals * 100 / total_intervals` over comparable frames in matched regions.
- Average absolute deviation in cents.
- Match percentage.
- Higher percentage.
- Lower percentage.
- Tolerance used.
- Metrics exclude non-similar additional portions left out of comparison.

Highest deviation points are out of scope for MVP.

### FS-18: Clear Session and Temporary Files

The app shall provide a Clear control and clean up session data.

Acceptance criteria:

- Clear button is visible on the single-page UI.
- Clear calls `POST /api/v1/session/clear`, resets UI, restores tolerance to 0, and deletes all temporary session files.
- Error popup dismissal performs the same reset and temp-file deletion.

### FS-17: Do Not Provide Coaching Feedback

The MVP shall not generate qualitative coaching advice.

Examples excluded:

- "Practice this phrase again."
- "You are mostly matching."
- "Your Re is weak."

The MVP shows graph comparison and statistical analysis only.
