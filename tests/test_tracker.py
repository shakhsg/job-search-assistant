def test_cannot_mark_applied_without_manual_confirmation(logged_in_client, app):
    logged_in_client.post(
        "/jobs/manual",
        data={
            "company": "Acme",
            "title": "Data Analyst",
            "location": "Singapore",
            "employment_type": "Full-time",
            "compensation": "",
            "source_url": "",
            "application_url": "https://example.com/apply",
            "description_raw": "Requirements\n- Python\n- SQL",
        },
        follow_redirects=True,
    )

    with app.app_context():
        from app.models import Application, Job
        from app.services.materials import MaterialGenerator
        from app.models import User

        user = User.query.filter_by(email="tester@example.com").first()
        job = Job.query.filter_by(company="Acme").first()
        application = MaterialGenerator().generate_for_job(user, job)
        application_id = application.id

    response = logged_in_client.post(
        f"/tracker/{application_id}/update",
        data={
            "status": "applied",
            "notes": "",
            "manual_review_confirmed": "y",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"personally submitted the application" in response.data


def test_export_csv_returns_rows(logged_in_client, app):
    response = logged_in_client.get("/tracker/export.csv")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"application_id,status,company,title" in response.data
