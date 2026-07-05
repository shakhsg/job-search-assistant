import io

import pytest

from app import create_app
from app.extensions import db
from app.models import Job, User
from app.repositories import ProfileRepository


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "REMOTE_FETCH_ENABLED": False,
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        user = User(email="tester@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        profile = ProfileRepository.get_or_create(user)
        profile.full_name = "Test User"
        profile.summary = "Python analyst with verified SQL and automation experience."
        profile.headline = "Python Analyst"
        profile.years_experience = 4
        profile.target_roles = "Data Analyst\nPython Developer"
        profile.preferred_locations = "Singapore\nRemote"
        profile.core_skills = "Python\nSQL\nFlask\nTesting"
        profile.experience_highlights = "Built data pipelines\nAutomated recurring reports"
        db.session.commit()
        return user


@pytest.fixture
def logged_in_client(client, user):
    client.post(
        "/auth/login",
        data={"email": "tester@example.com", "password": "password123"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def sample_job(app, user):
    with app.app_context():
        job = Job(
            user_id=user.id,
            source_type="manual",
            company="Acme",
            title="Data Analyst",
            location="Singapore",
            description_raw=(
                "Responsibilities\n"
                "- Build analytics dashboards\n"
                "- Write Python and SQL queries\n"
                "Requirements\n"
                "- 3+ years of experience\n"
                "- Flask and testing experience"
            ),
        )
        db.session.add(job)
        db.session.commit()
        return job


@pytest.fixture
def csv_upload():
    return {
        "csv_file": (io.BytesIO(b"company,title,location,description\nAcme,Analyst,Singapore,Python SQL testing"), "jobs.csv")
    }
