# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This is a single-file Python/Streamlit application (Centergy Group Project Success Simulator – PSSA v5.6). The entire app is in `app.py` (~351 lines). It uses Supabase for authentication and data persistence.

### Running the app

```bash
streamlit run app.py --server.port 8501 --server.headless true
```

Ensure `~/.local/bin` is on PATH (that's where `pip install --user` places the `streamlit` binary).

### External dependency: Supabase

The app requires a Supabase project with Auth enabled and two tables (`projects`, `feedback`). Credentials must be in `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://<project>.supabase.co"
SUPABASE_KEY = "<anon-key>"
```

Without valid Supabase credentials the app UI will load but login/signup and all data operations will fail with connection errors.

### Linting

No linter is configured in the repo. You can run `python3 -m pyflakes app.py` for basic checks. Existing warnings about f-strings without placeholders are pre-existing and non-blocking.

### Testing

No automated test suite exists in this repository. Manual testing is done by running the Streamlit app and interacting with the UI.
