def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Ada Analyst",
            "email": "ada@example.com",
            "password": "secure-password-123",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["full_name"] == "Ada Analyst"
    assert data["email"] == "ada@example.com"
    assert data["role"] == "analyst"
    assert "password" not in data
    assert "password_hash" not in data


def test_cannot_register_duplicate_email(client, registered_user):
    response = client.post(
        "/api/auth/register",
        json=registered_user,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "An account with this email already exists."


def test_login_and_get_current_user(client, registered_user):
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == registered_user["email"]


def test_protected_endpoint_rejects_missing_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401