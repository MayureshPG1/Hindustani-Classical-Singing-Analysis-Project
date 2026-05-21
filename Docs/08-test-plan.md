# Test Plan

## Test Goals

The MVP test plan verifies:

- Audio files are loaded and validated correctly.
- Full timeline is preserved.
- Pitch extraction produces usable frames.
- Sa detection works on representative recordings.
- Relative comparison works when guru and disciple use different scales.
- Different-duration clips can still be compared when they contain similar portions.
- Non-similar additional portions are excluded from comparison and scoring.
- Tolerance classification works.
- API returns stable schemas.
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
- Rejects unsupported formats (e.g. M4A).
- Converts stereo to mono.
- Resamples to 22050 Hz.
- Preserves leading silence.
- Preserves trailing silence.
- Rejects files longer than 2 minutes.
- Rejects unreadable file.

### Pitch Extractor

Test cases:

- Extracts F0 from synthetic sine wave.
- Marks silent region as unvoiced.
- Preserves frame count across silence.
- Returns confidence or voiced probability.
- Handles no-pitch audio without crash.

### Sa Detector

Test cases:

- Detects Sa from synthetic stable pitch.
- Detects Sa independently for two different pitch scales.
- Ignores low-confidence/unvoiced frames for Sa estimation.
- Returns failure or low confidence when pitch data is insufficient.

### Swara Mapper

Test cases:

- Maps Sa to `S`.
- Maps Komal Re to `r`.
- Maps Shuddha Re to `R`.
- Maps Komal Ga to `g`.
- Maps Shuddha Ga to `G`.
- Maps Shuddha Ma to `m`.
- Maps Tivra Ma to `M`.
- Maps Pa to `P`.
- Maps Komal Dha to `d`.
- Maps Shuddha Dha to `D`.
- Maps Komal Ni to `n`.
- Maps Shuddha Ni to `N`.

### Aligner

Test cases:

- Aligns identical contours.
- Aligns same contour at slower speed.
- Finds similar portions when guru and disciple clips have different durations.
- Excludes extra non-similar material from either recording.
- Returns no-match failure when no similar pitch-contour portion exists.
- Handles missing/unvoiced frames.
- Does not delete original time references.

### Scorer

Test cases:

- Difference within tolerance is `match`.
- Disciple above tolerance is `higher`.
- Disciple below tolerance is `lower`.
- Missing pitch is `unknown`.
- Percentages sum to expected values.
- `overall_score` equals `total_matching_intervals * 100 / total_intervals`.

## API Tests

### Health

- `GET /api/v1/health` returns status `ok`.

### Tolerance Settings

- `GET /api/v1/settings/tolerance` returns current tolerance settings.
- `PUT /api/v1/settings/tolerance` updates tolerance.
- Invalid tolerance returns `invalid_tolerance`.

### Clear Session

- `POST /api/v1/session/clear` clears temporary data and returns `status: cleared`.

### Audio Inspect

- Valid file returns metadata.
- Unsupported file returns `unsupported_file_type`.
- Long file returns `file_too_long`.
- Empty decoded audio returns `no_audio_detected`.
- Decode failure returns `decode_failed`.

### Compare

- Valid guru and disciple files return `ComparisonResult`.
- Response includes `guru_sa_hz`, `disciple_sa_hz`, `tolerance_cents`, frames, and metrics.
- Different absolute scales still produce relative comparison.
- Different durations still compare when similar portions exist.
- Response includes matched segments and excluded ranges when extra portions are left out.
- Invalid tolerance returns `invalid_tolerance` (outside 0–25).
- No vocals returns `no_vocals_detected`.
- No similar pattern returns `no_matching_pattern`.

## Frontend Tests

Use `pytest-qt` where practical.

Test cases:

- App window opens.
- Upload buttons exist.
- Tolerance defaults to 0.
- Plus button increments by 5 (max 25).
- Minus button decrements by 5 (min 0).
- Client-side validation runs before API inspect.
- Clear deletes temp files and resets tolerance to 0.
- Compare is disabled until both files are valid.
- Error message displays when backend returns error.
- Error appears as a popup.
- Dismissing an error popup resets the UI to the starting state.
- Summary panel updates after successful comparison.

## Integration Tests

Test full backend pipeline using generated fixtures:

1. Guru sine phrase at one Sa.
2. Disciple sine phrase at different Sa but same relative contour.
3. Disciple phrase shifted higher by known cents.
4. Disciple phrase shifted lower by known cents.
5. Files with leading and trailing silence.
6. Different-duration files with one shared phrase and extra material in one file.
7. Files with no matching melodic pattern.

Expected:

- Relative comparison works across different Sa values.
- Higher/lower classifications match known offsets.
- Silence remains represented.
- Similar shared phrase is compared even when durations differ.
- Extra non-similar portions are excluded from metrics.
- No shared pattern returns a specific error.

## Performance Tests

Targets:

- Files under 2 minutes process in 30 seconds or less on a typical laptop.
- UI remains responsive during processing.
- Backend does not exceed reasonable memory usage for two 2-minute mono files.

## Manual QA Checklist

- Launch app from development environment.
- Upload guru WAV.
- Upload disciple WAV.
- Adjust tolerance.
- Compare.
- Verify graph renders.
- Verify swara labels render.
- Verify metrics render.
- Try invalid file.
- Try file longer than 2 minutes.
- Try empty/no-audio file.
- Try audio with no vocals.
- Try two files with no matching pattern.
- Try file with silence.
- Confirm errors show as popups and reset the UI after dismissal.
- Close app and confirm backend process exits.

## Acceptance Criteria

MVP is test-complete when:

- Core unit tests pass.
- API tests pass.
- Main UI workflow works manually.
- Synthetic comparison fixtures produce expected classifications.
- No known crash exists for invalid files, no-pitch files, or backend errors.
