from httpx import AsyncClient

from src.core.database.models.user_model import User
from tests.auth.conftest import TEST_USER_PASSWORD


async def test_login_success(
    client: AsyncClient,
    test_user: User,
) -> None:
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged in"}
    assert "access_token" in client.cookies
    assert client.cookies["access_token"]


async def test_login_sets_httponly_cookie(
    client: AsyncClient,
    test_user: User,
) -> None:
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 200

    set_cookie = response.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "HttpOnly" in set_cookie


async def test_login_incorrect_password(
    client: AsyncClient,
    test_user: User,
) -> None:
    response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_login_unknown_user(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}


async def test_login_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "invalid-email", "password": "password123"},
    )
    assert response.status_code == 422


async def test_login_missing_password(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "login@example.com"},
    )
    assert response.status_code == 422
