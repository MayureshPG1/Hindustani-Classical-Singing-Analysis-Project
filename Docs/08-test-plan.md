# Test Plan

## Test Goals

The MVP test plan verifies:

- Audio files are loaded and validated correctly.
- Full timeline is preserved in pitch extraction.
- Pitch extraction produces usable frames.
- Compare API returns stable schemas with guru and disciple pitch arrays.
- UI can complete the main workflow.
- App handles errors with popups, then resets to the starting state.

## Test Tools

- `pytest`
- `pytest-cov`
- `pytest-qt`
- FastAPI `TestClient` or `httpx`
- Generated synthetic audio fixtures
- Small curated vocal samples where available

## Unit Tests

### Audio Loader

Test cases:

- Loads WAV file.
- Loads MP3 file if decoder is available.
- Loads M4A file if decoder is available.
- Rejects unsupported formats (e.g. FLAC).
- Converts stereo to mono.
- Resamples to 22050 Hz.
- Preserves leading silence.
- Preserves trailing silence.
- Rejects files longer than 5 minutes.
- Rejects unreadable file.

### Pitch Extractor

Test cases:

- Extracts F0 from synthetic sine wave.
- Marks silent region as unvoiced.
- Preserves frame count across silence.
- Returns confidence or voiced probability.
- Handles no-pitch audio without crash.
- Returns `no_vocals_detected` when voiced fraction is below threshold.

### Compare Service (when implemented)

Test cases:

- Returns both `guru_pitch_frames` and `disciple_pitch_frames`.
- Frame times start at 0 and advance by hop for each file.
- Unvoiced frames have null `frequency_hz`.
- Different-duration inputs both return full timelines.

## API Tests

### Health

- `GET /api/v1/health` returns status `ok`.

### Clear Session

- `POST /api/v1/session/clear` clears temporary data and returns `status: cleared`.

### Audio Inspect

- Valid file returns `file_info` and `pitch_metadata`.
- `preview_frames` length is 5 (or fewer if timeline is shorter).
- `total_frame_count` can exceed preview length.
- Unsupported file returns `unsupported_file_type`.
- Sparse pitch returns `no_vocals_detected`.
- Long file returns `file_too_long`.
- Empty decoded audio returns `no_audio_detected`.
- Decode failure returns `decode_failed`.

### Compare

- Valid guru and disciple files return `ComparisonResult`.
- Response includes `guru_pitch_frames` and `disciple_pitch_frames`.
- Voiced sine fixtures produce expected `frequency_hz` near target.
- No vocals returns `no_vocals_detected`.
- Missing or corrupt file returns appropriate structured error.

## Frontend Tests

Use `pytest-qt` where practical.

Test cases:

- App window opens.
- Upload buttons exist.
- Client-side validation runs before API inspect.
- Clear deletes temp files and resets UI.
- Compare is disabled until both files are valid.
- Error message displays when backend returns error.
- Error appears as a popup.
- Dismissing an error popup resets the UI to the starting state.
- Graph shows two series after successful comparison.

## Integration Tests

Test full backend pipeline using generated fixtures:

1. Guru sine phrase at fixed frequency.
2. Disciple sine phrase at different frequency.
3. Files with leading and trailing silence.
4. Different-duration files (both return pitch; no alignment required).
5. File with no usable pitch → `no_vocals_detected`.

Expected:

- Compare returns two pitch arrays.
- Silence remains represented as unvoiced frames.
- No Sa, swara, or scoring fields in response.

## Performance Tests

Targets:

- Files up to 5 minutes process within a reasonable time on a typical laptop.
- UI remains responsive during processing.
- Backend does not exceed reasonable memory usage for two 5-minute mono files.

## Manual QA Checklist

- Launch app from development environment.
- Upload guru WAV.
- Upload disciple WAV.
- Compare.
- Verify dual F0 graph renders (Hz vs seconds).
- Verify guru and disciple lines are distinct.
- Try invalid file.
- Try file longer than 5 minutes.
- Try empty/no-audio file.
- Try audio with no vocals.
- Confirm errors show as popups and reset the UI after dismissal.
- Clear session and confirm state resets.
- Close app and confirm backend process exits.

## Acceptance Criteria

MVP is test-complete when:

- Core unit tests pass.
- API tests pass.
- Main UI workflow works manually.
- Synthetic fixtures produce expected F0 in compare response.
- No known crash exists for invalid files, no-pitch files, or backend errors.

## Out of scope for MVP (tests to be added later)

When Hindustani comparison features return, add tests for:

- **Sa detector:** stable pitch histogram; independent guru/disciple Sa; `sa_detection_failed`.
- **Swara mapper:** all symbols `S r R g G m M P d D n N`; 100-cent bins.
- **Matched-portion finder:** similar windows; merge; `no_matching_pattern`; exclude extra material.
- **Aligner / DTW:** identical and tempo-shifted contours within a segment.
- **Scorer:** match/higher/lower/unknown vs tolerance; `overall_score` formula.
- **API:** tolerance get/set; `GET /swara-map`; compare with `tolerance_cents` and full `ComparisonResult` fields.
- **Integration:** same contour at different Sa; known cent offset → classification; different-duration matched phrase.
- **Frontend:** tolerance +/- controls; swara axis; match/higher/lower graph regions; summary metrics panel.
- **Manual QA:** tolerance adjust; different-scale compare; no matching pattern; Sa detection failure.
