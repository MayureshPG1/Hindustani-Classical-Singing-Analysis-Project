# UX Spec

## UX Goal

The app should feel like a focused practice tool: open it, upload two files, set tolerance if needed, compare, and inspect the graph. The first screen is the actual app, not a landing page.

## Page Model

The MVP has one page only.

Primary regions:

- Header/title area.
- Upload controls.
- Tolerance control.
- Compare action.
- File status area.
- Processing status area.
- Graph area.
- Summary statistics area.
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

3. Control and summary row:
   - `Upload Guru Voice` button.
   - Guru file status.
   - `Upload Disciple Voice` button.
   - Disciple file status.
   - `Tolerance` numeric field.
   - Minus and plus controls.
   - `Compare` button.
   - `Clear` button (required for MVP).
   - Summary statistics panel as part of this same row.

4. Bottom/status area:
   - Processing status.
   - Non-error status text only.

## Controls

### Upload Guru Voice

Behavior:

- Opens file picker.
- Accepts WAV and MP3 only.
- Runs client-side checks (extension, readable file, size > 0, duration ≤ 120 s when available) before calling the API.
- Updates guru file status after `POST /audio/inspect`.
- Shows validation errors as popups and resets UI after dismissal.

### Upload Disciple Voice

Behavior:

- Opens file picker.
- Accepts WAV and MP3 only.
- Runs client-side checks (extension, readable file, size > 0, duration ≤ 120 s when available) before calling the API.
- Updates disciple file status after `POST /audio/inspect`.
- Shows validation errors as popups and resets UI after dismissal.

### Tolerance

Behavior:

- Numeric editable field.
- Default value is 0.
- Valid range 0 to 25 cents.
- Unit is cents.
- Minus button decrements by 5 (not below 0).
- Plus button increments by 5 (not above 25).
- Value used for next comparison.

Display:

- Label: `Tolerance`
- Unit display: `cents`
- Example: `Tolerance [-] [0] [+] cents`

### Compare

Behavior:

- Disabled until both files are valid.
- On click, starts analysis.
- Shows progress state.
- Prevents duplicate compare requests while processing.

### Clear

Required MVP behavior:

- Clears selected files, graph, metrics, and errors.
- Calls `POST /api/v1/session/clear`.
- Deletes all temporary session files.
- Restores tolerance to default 0.

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
- Detecting Sa.
- Finding matching portions.
- Aligning pitch contours.
- Calculating comparison.
- Generating graph.
- Complete.
- Error.

## Graph UX

Graph requirements:

- Guru line and disciple line must be visually distinct.
- Guru line should be the reference.
- Disciple line should overlay against the guru line.
- Match regions should be easy to identify.
- Higher and lower deviations should be visually different.
- Tolerance band should be visible around the guru contour.
- Silent/unvoiced sections should appear as gaps or muted regions.
- Y-axis should show Indian swara labels (fixed 100-cent bins).
- X-axis should show concatenated alignment index across matched segments (`aligned_time` 0…N−1), not full-upload wall-clock time.
- Graph displays matched similar portions only.
- Non-similar additional portions are left out of the comparison graph and statistics.

Recommended visual encoding:

- Guru contour: dark solid line.
- Disciple contour: contrasting solid line.
- Tolerance band: translucent neutral band around guru contour.
- Match region: green or neutral highlight.
- Disciple higher: warm highlight.
- Disciple lower: cool highlight.
- Unknown/unvoiced: greyed or broken line.

Hover tooltip and zoom/pan are deferred (not required for MVP).

## Summary Statistics UX

Summary statistics belong in the third row as part of the control and summary row. They should not sit beside the graph in the second row.

Required metrics:

- Overall score.
- Average deviation.
- Match percentage.
- Higher percentage.
- Lower percentage.
- Tolerance used.

Labeling principles:

- Use plain labels.
- Do not add coaching text.
- Do not imply musical correctness beyond pitch-contour comparison.

## Error UX

Errors should be visible as popups.

Examples:

- Unsupported file type.
- File too long.
- Could not decode audio.
- No reliable pitch detected.
- Sa could not be detected.
- Backend not available.
- Analysis failed.
- No audio data found.
- No vocals detected.
- No matching vocal pattern found.

Error behavior:

- Show a modal popup with a clear message.
- After the user dismisses the popup, refresh/reset the UI to the starting state.
- Clear selected files, graph data, metrics, progress status, and validation state.
- Delete all temporary session files.
- Keep the app usable.
- User must start again by uploading both files.

## Empty State

Before comparison:

- Graph area may show a neutral placeholder such as "Upload guru and disciple audio to compare."
- No tutorial or long onboarding should be shown.

## Accessibility Notes

- Buttons and fields should have clear labels.
- Important graph states should be supported by labels or legend, not color alone.
- Text should remain readable at normal desktop window sizes.
- Controls should be keyboard reachable where practical.
