# User Journeys

## Personas

### Disciple

A Hindustani classical music student practicing outside class. They have a guru reference recording and their own attempt. They want to see where their pitch contour matches, goes higher, or goes lower than the guru.

### Guru

A teacher who may provide reference recordings to students. The guru may use the tool during or after lessons to help students visually understand pitch differences.

## Journey 1: Compare Two Clean Recordings

Goal: Disciple compares a guru reference with their own recording.

Preconditions:

- App is installed and opens locally on Windows.
- Guru audio file exists on the user's machine.
- Disciple audio file exists on the user's machine.
- Both files are supported formats and under 2 minutes.

Flow:

1. User opens the app.
2. User clicks `Upload Guru Voice`.
3. User selects the guru audio file.
4. App displays guru file name, duration, format, and validation status.
5. User clicks `Upload Disciple Voice`.
6. User selects the disciple audio file.
7. App displays disciple file name, duration, format, and validation status.
8. User leaves `Tolerance` at default `50` cents or edits it.
9. User clicks `Compare`.
10. App sends both files and tolerance to the local FastAPI backend.
11. Backend extracts pitch contours, detects Sa for both recordings, normalizes contours, finds similar portions, aligns them if needed, and computes comparison data.
12. Frontend renders guru and disciple pitch contours on the same graph.
13. App highlights matching, higher, and lower regions.
14. App displays statistical summary.

Success outcome:

- User sees a graph with guru and disciple pitch contours.
- User sees match, higher, and lower sections.
- User sees overall score, average deviation, match percentage, higher percentage, lower percentage, and tolerance used.

Algorithm expectation:

- Guru and disciple may or may not sing in different base Sa.
- This is not a separate user action or workflow.
- The backend must auto-detect Sa independently and normalize comparison regardless of whether both recordings use the same or different base Sa.

## Journey 2: Clips Have Different Durations

Goal: User compares two recordings where one clip contains extra material before or after the matching phrase.

Flow:

1. User uploads guru and disciple files.
2. Each file is 2 minutes or shorter, but the durations are different.
3. One recording may contain extra silence, setup time, repeated notes, or an additional phrase not present in the other recording.
4. User clicks `Compare`.
5. Backend processes both full files.
6. Backend finds similar pitch-contour portions between guru and disciple.
7. Backend compares only the matched similar portions.
8. Backend leaves out non-similar additional portions from comparison and scoring.
9. Frontend displays graph and statistics for the matched comparison region.

Success outcome:

- Different clip durations do not block comparison.
- Extra non-similar material from either uploaded audio is not scored.
- User sees comparison for the best matched similar portions.

## Journey 3: User Adjusts Tolerance

Goal: User wants stricter or more forgiving comparison.

Flow:

1. User uploads both files.
2. User changes `Tolerance` using plus/minus controls or direct input.
3. Plus/minus controls change tolerance by 10 cents per click.
4. User clicks `Compare`.
5. Backend classifies frames using the selected tolerance.

Success outcome:

- Lower tolerance produces fewer matching sections.
- Higher tolerance produces more matching sections.
- Result displays the tolerance used.

## Journey 4: Recording Contains Silence or Long Ending

Goal: User compares files that include pauses, silence, or long phrase endings.

Flow differences:

1. Backend loads full audio.
2. Backend does not trim leading silence, trailing silence, long endings, or non-vocal silent sections.
3. Backend marks silent or unvoiced regions in analysis data.
4. Graph shows gaps or muted regions rather than hiding them.

Success outcome:

- Timeline still represents the full uploaded recording.
- Silent regions do not create misleading pitch lines.

## Journey 5: Invalid File

Goal: User accidentally uploads an unsupported or unreadable file.

Flow:

1. User clicks upload.
2. User selects invalid file.
3. App attempts validation through the backend or local file metadata checks.
4. App displays a clear error popup.
5. After the user dismisses the popup, the UI resets to the starting state.

Expected error examples:

- Unsupported file type.
- File is unreadable.
- File duration is longer than 2 minutes.
- No detectable vocal pitch.

Recovery:

- User starts again by uploading files.
- App does not crash.

## Journey 6: Backend Processing Error

Goal: App handles unexpected analysis failure.

Flow:

1. User uploads both files and clicks `Compare`.
2. Backend fails during decoding, pitch extraction, Sa detection, or alignment.
3. API returns a structured error.
4. Frontend displays a useful error popup.
5. After the user dismisses the popup, the UI resets to the starting state.

Success outcome:

- App remains usable.
- User starts again by uploading files and running comparison.
