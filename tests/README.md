# Tests layout

- `test_imports.py` — Phase 0 smoke imports.
- `backend/` — backend unit/API tests (Phase 1+). **No `__init__.py`** here (would shadow the `backend` package).
- `frontend/` — frontend tests (Phase 7+). **No `__init__.py`** here (would shadow the `frontend` package).
- `fixtures/` — synthetic audio helpers (later phases).
