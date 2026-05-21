# User Journeys

## Personas

### Disciple

A Hindustani classical music student practicing outside class. They have a guru reference recording and their own attempt. They want to see both pitch contours overlaid so they can visually compare melodic shape.

### Guru

A teacher who may provide reference recordings to students. The guru may use the tool during or after lessons to help students see pitch movement side by side.

## Journey 1: Compare Two Clean Recordings

Goal: Disciple compares a guru reference with their own recording.

Preconditions:

- App is installed and opens locally on Windows.
- Guru audio file exists on the user's machine.
- Disciple audio file exists on the user's machine.
- Both files are supported formats and under 5 minutes.

Flow:

1. User opens the app.
2. User clicks `Upload Guru Voice`.
3. User selects the guru audio file.
4. App displays guru file name, duration, format, and validation status.
5. User clicks `Upload Disciple Voice`.
6. User selects the disciple audio file.
7. App displays disciple file name, duration, format, and validation status.
8. User clicks `Compare`.
9. App sends both files to the local FastAPI backend.
10. Backend extracts pitch contours for each recording.
11. Frontend renders guru and disciple F0 lines on the same graph (Hz vs time).

Success outcome:

- User sees two distinct pitch contour lines for guru and disciple.
- User can visually compare shape, register, and timing at a glance.

Note:

- Guru and disciple may sing in different keys; Hz overlay does not normalize scale.
- Clips with different durations share one time axis from 0; lines end when each recording ends.

## Journey 2: Clips Have Different Durations

Goal: User compares two recordings of different length.

Flow:

1. User uploads guru and disciple files.
2. Each file is 5 minutes or shorter, but durations differ.
3. User clicks `Compare`.
4. Backend processes both full files and returns full pitch timelines.
5. Frontend plots both contours on wall-clock time (each line spans its own duration).

Success outcome:

- Different durations do not block comparison.
- User sees both full pitch traces without automatic phrase alignment.

## Journey 3: Recording Contains Silence or Long Ending

Goal: User compares files that include pauses, silence, or long phrase endings.

Flow:

1. Backend loads full audio without trimming.
2. Backend marks silent or unvoiced regions in pitch data.
3. Graph shows gaps or breaks where F0 is not plotted.

Success outcome:

- Timeline still represents the full uploaded recording.
- Silent regions do not create misleading pitch lines.

## Journey 4: Invalid File

Goal: User accidentally uploads an unsupported or unreadable file.

Flow:

1. User clicks upload.
2. User selects invalid file.
3. App validates through client checks and/or backend inspect.
4. App displays a clear error popup.
5. After the user dismisses the popup, the UI resets to the starting state.

Expected error examples:

- Unsupported file type.
- File is unreadable.
- File duration is longer than 5 minutes.
- No detectable vocal pitch.

Recovery:

- User starts again by uploading files.
- App does not crash.

## Journey 5: Backend Processing Error

Goal: App handles unexpected analysis failure.

Flow:

1. User uploads both files and clicks `Compare`.
2. Backend fails during decoding or pitch extraction.
3. API returns a structured error.
4. Frontend displays a useful error popup.
5. After the user dismisses the popup, the UI resets to the starting state.

Success outcome:

- App remains usable.
- User starts again by uploading files and running comparison.

## Out of scope for MVP (journeys to be added later)

These workflows existed in the prior spec and are **not** part of the minimal pitch-overlay MVP:

- **Adjust tolerance:** change 0–25 cents before compare; stricter/forgiving match classification.
- **Different keys via Sa:** backend normalizes both recordings to detected Sa; user does not pick Sa manually.
- **Different durations with phrase match:** backend finds similar portions, compares only those, excludes extra material from graph and score.
- **No matching pattern:** compare fails with `no_matching_pattern` when recordings share no similar contour.
- **Sa detection failure:** compare fails with `sa_detection_failed`.
- **Scored outcome:** user sees overall score, match/higher/lower percentages, and tolerance used after compare.
