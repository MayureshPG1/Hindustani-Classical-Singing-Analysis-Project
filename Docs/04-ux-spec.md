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
- Comparison metrics panel (after Compare).
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

3. Control row (third row):
   - **Left bordered cluster:** `Upload Guru Voice`, guru file status, `Upload Disciple Voice`, disciple file status, `Compare`, and `Clear`.
   - **Right bordered cluster (fixed width):** comparison metrics panel (see below).
   - Clusters are visually separated (border + background) so the row height stays stable when metrics appear.

4. Bottom/status area (fourth row):
   - Processing status.
   - Non-error status text only.

Tolerance controls are **not** part of MVP.

## Controls

### Upload Guru Voice

Behavior:

- Opens file picker.
- Accepts WAV, MP3, and M4A.
- Runs client-side checks (extension, readable file, size > 0, duration ≤ 300 s when available) before calling the API.
- Updates guru file status from `POST /audio/inspect` (`file_info` + `pitch_metadata` stats).
- Shows validation errors as popups and resets UI after dismissal.

### Upload Disciple Voice

Behavior:

- Opens file picker.
- Accepts WAV, MP3, and M4A.
- Runs client-side checks before calling the API.
- Updates disciple file status from `POST /audio/inspect` (`file_info` + `pitch_metadata` stats).
- Shows validation errors as popups and resets UI after dismissal.

### Compare

Behavior:

- Disabled until both files are valid.
- On click, starts analysis.
- Shows progress state.
- Prevents duplicate compare requests while processing.
- On success, populates the comparison metrics panel (third row, bottom-right) from `comparison_summary`.

### Clear

Required MVP behavior:

- Clears selected files, graph, comparison metrics, and errors.
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
- Match / higher / lower region coloring on the graph.
- Error popups: Sa could not be detected; no matching vocal pattern found.

## Comparison Metrics Panel (MVP)

Location: **third row, bottom-right** (same row as upload controls and Compare/Clear).

Visibility:

- Before Compare: placeholder text (e.g. “Comparison metrics appear here after Compare.”).
- After successful Compare: show values from `comparison_summary`.
- After Clear or error reset: return to placeholder.

Fields (labels user-facing):

| Label | API field | Format |
| --- | --- | --- |
| Match score | `overall_score` | Percent, one decimal (same as match share of scored pairs). |
| Avg deviation | `average_deviation_cents` | Cents, one decimal. |
| Match | `match_percentage` | Percent, one decimal. |
| Higher | `higher_percentage` | Percent, one decimal. |
| Lower | `lower_percentage` | Percent, one decimal. |
| Tolerance | `tolerance_cents` | Integer cents used for classification (default 0). |

No tolerance editor in MVP; tolerance is shown read-only from the compare response.

Per-file duration and voiced fraction remain on the guru/disciple status lines after inspect (not in this panel).

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
