from app.models import User


def test_register_hashes_password(client, app):
    response = client.post(
        "/auth/register",
        data={
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.check_password("password123")
