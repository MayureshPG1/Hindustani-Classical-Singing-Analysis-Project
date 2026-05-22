# Hindustani Classical Singing Analysis

Local Windows desktop MVP for comparing guru and disciple vocal recordings (pitch contours relative to detected Sa).

## Requirements

- Python 3.11.x
- Windows (first target)

## Setup

```powershell
cd "path\to\Hindustani-Classical-Singing-Analysis-Project"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Verify (Phase 0)

```powershell
pytest tests/test_imports.py -v
```

## Backend URL (MVP)

`http://127.0.0.1:8765/api/v1`

## Run backend

```powershell
.\.venv\Scripts\Activate.ps1
$env:HCSA_VERBOSE = "1"
.\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8765 --log-level info
```

Verbose route logging (step timings, pitch stats) is enabled when any of these is set:

- Environment: `HCSA_VERBOSE=1`
- Query: `?verbose=true` (e.g. `POST /api/v1/audio/inspect?verbose=true`)
- Header: `X-HCSA-Verbose: 1`

API errors are always logged at WARNING. Routine success paths log only in verbose mode.

## Documentation

See [`Docs/`](Docs/) for the full spec pack. Implementation order: [`Docs/09-implementation-plan.md`](Docs/09-implementation-plan.md).
