# UX Spec

## UX Goal

The app should feel like a focused practice tool: open it, upload two files, compare, and inspect the pitch overlay. The first screen is the actual app, not a landing page.

## Page Model

The MVP has one page only.

Primary regions:

- Header/title area.
- Upload controls.
- Compare action.
- File status area.
- Processing status area.
- Graph area.
- Optional lightweight summary (durations / voiced stats).
- Error popup.

## Layout

Recommended desktop layout:

1. Top row:
   - App title.
   - Optional compact subtitle: "Guru vs Disciple Pitch Comparison".

2. Graph row:
   - Graph area only.
   - The graph should take the main visual focus of the screen.
   - Before comparison, the graph row may show the empty-state placeholder.

3. Control row:
   - `Upload Guru Voice` button.
   - Guru file status.
   - `Upload Disciple Voice` button.
   - Disciple file status.
   - `Compare` button.
   - `Clear` button (required for MVP).
   - Optional compact summary (durations, voiced fraction).

4. Bottom/status area:
   - Processing status.
   - Non-error status text only.

Tolerance controls are **not** part of MVP.

## Controls

### Upload Guru Voice

Behavior:

- Opens file picker.
- Accepts WAV and MP3 only.
- Runs client-side checks (extension, readable file, size > 0, duration ≤ 300 s when available) before calling the API.
- Updates guru file status from `POST /audio/inspect` (`file_info`; optional pitch preview for debug).
- Shows validation errors as popups and resets UI after dismissal.

### Upload Disciple Voice

Behavior:

- Opens file picker.
- Accepts WAV and MP3 only.
- Runs client-side checks before calling the API.
- Updates disciple file status from `POST /audio/inspect` (`file_info`; optional pitch preview).
- Shows validation errors as popups and resets UI after dismissal.

### Compare

Behavior:

- Disabled until both files are valid.
- On click, starts analysis.
- Shows progress state.
- Prevents duplicate compare requests while processing.

### Clear

Required MVP behavior:

- Clears selected files, graph, summary, and errors.
- Calls `POST /api/v1/session/clear`.
- Deletes all temporary session files.

## File Status Display

For each uploaded file, show:

- File name.
- Duration.
- Format.
- Validation state.

Validation states:

- Empty.
- Loading.
- Valid.
- Invalid.

## Processing States

Supported states:

- Idle.
- Loading audio.
- Extracting pitch.
- Generating graph.
- Complete.
- Error.

## Graph UX

Graph requirements:

- Guru line and disciple line must be visually distinct.
- Guru line should be the reference style (e.g. darker solid).
- Disciple line overlays on the same axes.
- Y-axis: Hz (linear).
- X-axis: seconds (`time_seconds`).
- Full timeline for each recording (lines may end at different times if durations differ).
- Silent/unvoiced sections appear as gaps or breaks (no F0 plotted).

Recommended visual encoding:

- Guru contour: dark solid line.
- Disciple contour: contrasting solid line.
- Unvoiced: gap or no line segment.

No tolerance band, match/higher/lower highlights, or swara tick labels in MVP.

Hover tooltip and zoom/pan are deferred (not required for MVP).

## Out of scope for MVP (UX to be added later)

- Tolerance numeric field and +/- controls (0–25 cents, step 5).
- Processing states: detecting Sa, finding matching portions, aligning, calculating comparison.
- Y-axis Indian swara labels (100-cent bins).
- X-axis concatenated `aligned_time` (matched segments only).
- Tolerance band around guru contour.
- Match / higher / lower region coloring.
- Summary panel: overall score, average deviation, match/higher/lower percentages, tolerance used.
- Error popups: Sa could not be detected; no matching vocal pattern found.

## Summary UX (Optional)

If shown, keep minimal:

- Guru duration and disciple duration.
- Optional voiced frame count or voiced percentage per file.

Do not show overall match score, deviation percentages, or tolerance used.

## Error UX

Errors should be visible as popups.

Examples:

- Unsupported file type.
- File too long.
- Could not decode audio.
- Backend not available.
- Analysis failed.
- No audio data found.
- No vocals detected.

Error behavior:

- Show a modal popup with a clear message.
- After the user dismisses the popup, refresh/reset the UI to the starting state.
- Clear selected files, graph data, summary, progress status, and validation state.
- Delete all temporary session files.
- Keep the app usable.
- User must start again by uploading both files.

## Empty State

Before comparison:

- Graph area may show a neutral placeholder such as "Upload guru and disciple audio to compare."
- No tutorial or long onboarding should be shown.

## Accessibility Notes

- Buttons and fields should have clear labels.
- Guru vs disciple lines should be distinguishable by style and legend, not color alone.
- Text should remain readable at normal desktop window sizes.
- Controls should be keyboard reachable where practical.
