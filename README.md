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

## Documentation

See [`Docs/`](Docs/) for the full spec pack. Implementation order: [`Docs/09-implementation-plan.md`](Docs/09-implementation-plan.md).
