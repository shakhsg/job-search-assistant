from app.models import Application


def test_generating_materials_requires_manual_review_flow(logged_in_client, app):
    logged_in_client.post(
        "/jobs/manual",
        data={
            "company": "Acme",
            "title": "Backend Developer",
            "location": "Remote",
            "employment_type": "Full-time",
            "compensation": "",
            "source_url": "",
            "application_url": "https://example.com/apply",
            "description_raw": "Requirements\n- Python\n- Flask\n- SQL",
        },
        follow_redirects=True,
    )

    with app.app_context():
        from app.models import Job

        job = Job.query.filter_by(company="Acme", title="Backend Developer").first()

    response = logged_in_client.post(
        f"/materials/generate/{job.id}",
        data={},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Nothing has been submitted automatically" in response.data

    with app.app_context():
        application = Application.query.filter_by(job_id=job.id).first()
        assert application is not None
        assert application.status == "review_pending"
        assert application.manual_submission_confirmed is False
        assert "This draft uses only information stored in your profile" in application.truthfulness_notes
