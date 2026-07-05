def test_manual_job_creation_scores_against_profile(logged_in_client, app):
    response = logged_in_client.post(
        "/jobs/manual",
        data={
            "company": "Acme",
            "title": "Data Analyst",
            "location": "Singapore",
            "employment_type": "Full-time",
            "compensation": "",
            "source_url": "",
            "application_url": "https://example.com/apply",
            "description_raw": (
                "Responsibilities\n- Build dashboards\nRequirements\n- Python\n- SQL\n- Testing"
            ),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Match score" in response.data
    assert b"Skill overlap" in response.data


def test_csv_import_creates_jobs(logged_in_client, app, csv_upload):
    response = logged_in_client.post(
        "/jobs/ingest/csv",
        data=csv_upload,
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Imported 1 job rows from CSV." in response.data
