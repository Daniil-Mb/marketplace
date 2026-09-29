from httpx import AsyncClient

from src.core.database.models.user_model import User
from tests.auth.conftest import TEST_USER_PASSWORD


async def test_get_current_user(
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

    response = await client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()
    assert str(data["id"]) == str(test_user.id)
    assert data["email"] == test_user.email


async def test_get_current_user_without_auth(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code == 401
