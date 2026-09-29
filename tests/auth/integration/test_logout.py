from httpx import AsyncClient

from src.core.database.models.user_model import User
from tests.auth.conftest import TEST_USER_PASSWORD


async def test_logout(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert login_response.status_code == 200
    assert "access_token" in client.cookies

    logout_response = await client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "Successfully logged out"}
    assert "access_token" not in client.cookies


async def test_logout_removes_cookie_and_me_returns_401(
    client: AsyncClient,
    test_user: User,
) -> None:
    login_response = await client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": TEST_USER_PASSWORD,
        },
    )
    assert login_response.status_code == 200

    logout_response = await client.post("/auth/logout")
    assert logout_response.status_code == 200

    me_response = await client.get("/auth/me")
    assert me_response.status_code == 401
