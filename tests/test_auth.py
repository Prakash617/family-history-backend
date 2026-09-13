import pytest
from rest_framework import status

from apps.users.models import User


@pytest.mark.django_db
def test_user_registration(client):
    data = {
        "email": "testuser@familytree.local",
        "password": "Password123!",
        "password_confirm": "Password123!",
        "first_name": "Test",
        "last_name": "User",
    }
    response = client.post("/api/v1/auth/register/", data=data, content_type="application/json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"]["email"] == "testuser@familytree.local"
    assert User.objects.filter(email="testuser@familytree.local").exists()


@pytest.mark.django_db
def test_user_login(client):
    User.objects.create_user(email="login@familytree.local", password="SecretPassword123!")
    response = client.post(
        "/api/v1/auth/login/",
        data={"email": "login@familytree.local", "password": "SecretPassword123!"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_current_user_me(client):
    User.objects.create_user(email="me@familytree.local", password="Password123!", first_name="John")
    login_res = client.post(
        "/api/v1/auth/login/",
        data={"email": "me@familytree.local", "password": "Password123!"},
        content_type="application/json",
    )
    token = login_res.data["access"]
    response = client.get("/api/v1/users/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == "me@familytree.local"
    assert response.data["first_name"] == "John"
