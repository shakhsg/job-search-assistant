# Job Search and Application Copilot

Manual-first Flask app for collecting jobs, scoring them against a real profile, generating honest application materials, and tracking progress without blind auto-submission.

## Principles

- Truthfulness first: generated content is based on stored profile facts plus parsed job descriptions.
- Security first: hashed passwords, CSRF protection, validation, secure session settings, and SSRF-style URL checks for remote ingestion.
- Simple UI: Tailwind-powered screens focused on profile, jobs, materials, and tracker workflows.
- Reusable architecture: app factory, blueprints, services, repositories, forms, and models are split into clear modules.

## What is built

### Phase 1: Scaffold app

- Flask app factory in [app/__init__.py](/Users/shuhratmirzaev/Documents/New project/app/__init__.py)
- Modular folders for blueprints, forms, models, repositories, services, templates, static assets, scripts, and tests
- Tailwind-based UI shell in [app/templates/base.html](/Users/shuhratmirzaev/Documents/New project/app/templates/base.html)

### Phase 2: Auth + database

- SQLite models for users, profile, jobs, and applications
- Secure login with hashed passwords using Werkzeug
- CSRF protection via Flask-WTF
- Environment-driven config in [app/config.py](/Users/shuhratmirzaev/Documents/New project/app/config.py)

### Phase 3: Jobs CRUD + parsing

- Manual job CRUD flow
- Link ingestion with HTML extraction
- CSV ingestion
- Optional allowed API ingestion with provider adapters for `generic_json`, `greenhouse`, and `lever`
- Job description parser for skills, responsibilities, requirements, seniority, and work mode

### Phase 4: Scoring engine

- Transparent match scoring in [app/services/scoring.py](/Users/shuhratmirzaev/Documents/New project/app/services/scoring.py)
- Visible strengths, gaps, unknowns, and score components
- Rescoring when the profile changes

### Phase 5: Resume + cover letter generation

- Honest tailored resume draft
- Honest cover letter draft
- Application-answer preparation
- Truthfulness notes and review checklist

### Phase 6: Tracker dashboard

- Status-based tracker
- Manual review and manual submission confirmation gates
- CSV export

### Phase 7: Polish + tests + README

- Seed data
- Test suite for auth, jobs, materials, and tracker
- Setup and architecture documentation

## Folder structure

```text
app/
  blueprints/
  forms/
  models/
  repositories/
  services/
  static/
  templates/
scripts/
tests/
run.py
requirements.txt
```

## Quick start

1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment file and update secrets:

```bash
cp .env.example .env
```

4. Initialize the database:

```bash
python scripts/init_db.py
```

5. Seed demo data:

```bash
python scripts/seed_data.py
```

6. Run the app:

```bash
flask --app run.py run --debug
```

Demo login after seeding:

- Email: `demo@example.com`
- Password: `demo12345`

## Security notes

- Set a strong `SECRET_KEY` before any non-local deployment.
- `ALLOWED_API_HOSTS` must be configured before API ingestion is enabled.
- Remote ingestion rejects local and private hostnames to reduce SSRF risk.
- This app does not auto-submit jobs and should remain manual-first by design.
- Tailwind is loaded via CDN for simplicity. For production, pin and self-host compiled assets.

## CSV format

Expected columns can include:

- `company`
- `title`
- `location`
- `description`
- `source_url`
- `application_url`
- `employment_type`
- `compensation`
- `external_id`

## Testing

Run:

```bash
pytest
```

## Extension ideas

- Add resume versioning and downloadable DOCX/PDF exports
- Add structured experience tables instead of freeform profile text
- Add optional LLM-assisted drafting with strong fact-guardrails
- Add a PDF/portfolio ingestion pipeline if you want the referenced PDF incorporated later
