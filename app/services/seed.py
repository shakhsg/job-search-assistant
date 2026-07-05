from app.extensions import db
from app.models import User
from app.repositories import ProfileRepository
from app.services.ingest import JobIngestionService
from app.services.materials import MaterialGenerator
from app.services.scoring import MatchingEngine


def seed_demo_data(app) -> None:
    with app.app_context():
        existing = User.query.filter_by(email="demo@example.com").first()
        if existing:
            return

        user = User(email="demo@example.com")
        user.set_password("demo12345")
        db.session.add(user)
        db.session.commit()

        profile = ProfileRepository.get_or_create(user)
        profile.full_name = "Demo Candidate"
        profile.headline = "Python / Data / Product Operations"
        profile.email = user.email
        profile.phone = "+65 9000 0000"
        profile.location = "Singapore"
        profile.linkedin_url = "https://www.linkedin.com/in/demo-candidate"
        profile.summary = (
            "Builder with hands-on experience across Python automation, data workflows, "
            "operations, and stakeholder-facing product support."
        )
        profile.years_experience = 5
        profile.work_authorization = "Requires employer review for relocation and work authorization."
        profile.target_roles = "Data Analyst\nPython Developer\nOperations Analyst"
        profile.preferred_locations = "Singapore\nRemote"
        profile.must_have_keywords = "python\nsql\nanalytics"
        profile.avoid_keywords = "commission-only\nunpaid"
        profile.core_skills = "Python\nFlask\nSQL\nSQLite\nPandas\nAnalytics\nAutomation\nTesting"
        profile.experience_highlights = (
            "Built internal automation tools that reduced manual reporting time.\n"
            "Worked with stakeholders to translate operational needs into technical workflows.\n"
            "Created dashboards, data exports, and process documentation."
        )
        profile.education = "BSc in Information Systems"
        profile.achievements = (
            "Reduced reporting turnaround time by 40%.\n"
            "Delivered clean data exports used by leadership for weekly reviews."
        )
        profile.certifications = "Google Data Analytics"
        profile.answer_bank = "Open to hybrid work\nComfortable with async collaboration"
        db.session.commit()

        ingestion = JobIngestionService(app.config)
        matching = MatchingEngine()
        generator = MaterialGenerator()

        jobs = [
            {
                "company": "DBS",
                "title": "Data Analyst",
                "location": "Singapore",
                "employment_type": "Full-time",
                "source_type": "manual",
                "application_url": "https://example.com/apply/dbs-data-analyst",
                "description_raw": (
                    "Responsibilities\n"
                    "- Build reports and dashboards for operations teams\n"
                    "- Use Python and SQL to clean and analyze data\n"
                    "Requirements\n"
                    "- 3+ years of experience in analytics\n"
                    "- Strong SQL and stakeholder communication\n"
                    "Preferred\n"
                    "- Experience with Flask or internal tooling\n"
                ),
            },
            {
                "company": "Grab",
                "title": "Operations Analyst",
                "location": "Hybrid - Singapore",
                "employment_type": "Full-time",
                "source_type": "manual",
                "application_url": "https://example.com/apply/grab-ops-analyst",
                "description_raw": (
                    "What you'll do\n"
                    "- Partner with operations teams to improve workflows\n"
                    "- Automate weekly reporting in Python\n"
                    "Qualifications\n"
                    "- 2+ years of experience\n"
                    "- SQL, analytics, testing, and communication\n"
                ),
            },
            {
                "company": "Sea",
                "title": "Junior Backend Engineer",
                "location": "Onsite - Singapore",
                "employment_type": "Full-time",
                "source_type": "manual",
                "application_url": "https://example.com/apply/sea-backend",
                "description_raw": (
                    "Responsibilities\n"
                    "- Build backend services with Python and APIs\n"
                    "Requirements\n"
                    "- Internship or 1+ years of backend development\n"
                    "- Knowledge of Flask, SQL, and testing\n"
                ),
            },
        ]

        generated_application = None
        for payload in jobs:
            job = ingestion.create_manual_job(user, payload)
            matching.refresh_job(profile, job)
            if generated_application is None:
                generated_application = generator.generate_for_job(user, job)

        if generated_application:
            generated_application.notes = "Seeded demo application waiting for human review."
            db.session.commit()
