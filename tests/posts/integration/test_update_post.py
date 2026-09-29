from httpx import AsyncClient

from src.core.database.models.user_model import User


async def _create_post(client: AsyncClient, category_id: int) -> dict:
    response = await client.post(
        "/posts",
        data={
            "title": "Old title",
            "content": "Old content",
            "category_id": str(category_id),
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_update_post(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    created = await _create_post(authenticated_client, test_category.id)
    post_id = created["id"]
    old_updated_at = created["updated_at"]

    response = await authenticated_client.patch(
        f"/posts/{post_id}",
        data={"title": "New title"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "New title"
    assert data["content"] == "Old content"
    assert data["updated_at"] != old_updated_at


async def test_update_post_partial(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    created = await _create_post(authenticated_client, test_category.id)
    post_id = created["id"]

    response = await authenticated_client.patch(
        f"/posts/{post_id}",
        data={"content": "Only content updated"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Old title"
    assert data["content"] == "Only content updated"


async def test_user_cannot_update_other_users_post(
    client: AsyncClient,
    test_user: User,
    second_user: User,
    test_category,
) -> None:
    from tests.posts.conftest import (
        SECOND_USER_EMAIL,
        SECOND_USER_PASSWORD,
        TEST_USER_EMAIL,
        TEST_USER_PASSWORD,
    )

    await client.post(
        "/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    created = await _create_post(client, test_category.id)
    post_id = created["id"]

    await client.post("/auth/logout")

    await client.post(
        "/auth/login",
        json={
            "email": SECOND_USER_EMAIL,
            "password": SECOND_USER_PASSWORD,
        },
    )

    response = await client.patch(
        f"/posts/{post_id}",
        data={"title": "Hacked title"},
    )

    assert response.status_code == 403
