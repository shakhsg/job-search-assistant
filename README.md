# Job Search and Application Copilot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000000?logo=flask)](https://flask.palletsprojects.com)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?logo=tailwindcss)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-database-003B57?logo=sqlite)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CI](https://github.com/shakhsg/job-search-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/shakhsg/job-search-assistant/actions)

AI-powered job search copilot — collect, score, and track job applications with honest AI-generated resumes and cover letters. Built with Flask, SQLite, and Tailwind CSS.

**Author:** Shukhrat Mirzaev | **Skills:** Flask · SQLite · Tailwind CSS · REST API · Web Scraping · AI Prompting

---

## Principles

- **Truthfulness first** — generated content is based on stored profile facts plus parsed job descriptions.
- **Security first** — hashed passwords, CSRF protection, validation, secure session settings, and SSRF-style URL checks.
- **Simple UI** — Tailwind-powered screens focused on profile, jobs, materials, and tracker workflows.
- **Reusable architecture** — app factory, blueprints, services, repositories, forms, and models.

---

## What is built

### Phase 1: Scaffold app
- Flask app factory in [`app/__init__.py`](app/__init__.py)
- Modular folders for blueprints, forms, models, repositories, services, templates
- Tailwind-based UI shell in [`app/templates/base.html`](app/templates/base.html)

### Phase 2: Auth + database
- SQLite models for users, profile, jobs, and applications
- Secure login with hashed passwords using Werkzeug
- CSRF protection via Flask-WTF
- Environment-driven config in [`app/config.py`](app/config.py)

### Phase 3: Jobs CRUD + parsing
- Manual job CRUD flow
- Link ingestion with HTML extraction
- CSV ingestion
- Optional API ingestion with adapters for `generic_json`, `greenhouse`, and `lever`
- Job description parser for skills, responsibilities, requirements, seniority, and work mode

### Phase 4: Scoring engine
- Transparent match scoring in [`app/services/scoring.py`](app/services/scoring.py)
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

---

## Quick Start

```bash
# Clone
git clone https://github.com/shakhsg/job-search-assistant.git
cd job-search-assistant

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your secrets

# Initialize
python scripts/init_db.py
python scripts/seed_data.py

# Run
flask --app run.py run --debug
```

**Demo login:** `demo@example.com` / `demo12345`

---

## CSV Format

Expected columns: `company`, `title`, `location`, `description`, `source_url`, `application_url`, `employment_type`, `compensation`, `external_id`

---

## Testing

```bash
pytest
```

---

## Security Notes

- Set a strong `SECRET_KEY` before any non-local deployment
- `ALLOWED_API_HOSTS` must be configured before API ingestion
- Remote ingestion rejects local and private hostnames (SSRF protection)
- Manual-first by design — no auto-submission
- Tailwind via CDN for dev; pin and self-host for production

---

## Extension Ideas

- [ ] Resume versioning and downloadable DOCX/PDF exports
- [ ] Structured experience tables instead of freeform profile text
- [ ] Optional LLM-assisted drafting with fact-guardrails
- [ ] PDF/portfolio ingestion pipeline