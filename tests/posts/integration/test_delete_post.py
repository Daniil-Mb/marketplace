from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.deleted_post_model import DeletedPost
from src.core.database.models.post_model import Post
from src.core.database.models.user_model import User

async def _create_post(client: AsyncClient, category_id: int) -> dict:
    response = await client.post(
        "/posts",
        data={
            "title": "Post to delete",
            "content": "Delete me",
            "category_id": str(category_id),
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_delete_post_soft_deletes(
    authenticated_client: AsyncClient,
    db_session: AsyncSession,
    test_category,
) -> None:
    created = await _create_post(authenticated_client, test_category.id)
    post_id = created["id"]

    response = await authenticated_client.delete(f"/posts/{post_id}")

    assert response.status_code == 204

    post_result = await db_session.execute(
        select(Post).where(Post.id == post_id)
    )
    assert post_result.scalar_one_or_none() is None

    deleted_result = await db_session.execute(
        select(DeletedPost).where(
            DeletedPost.original_post_id == post_id,
        )
    )
    deleted = deleted_result.scalar_one_or_none()

    assert deleted is not None
    assert deleted.title == "Post to delete"


async def test_deleted_post_not_in_list(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    created = await _create_post(authenticated_client, test_category.id)
    post_id = created["id"]

    await authenticated_client.delete(f"/posts/{post_id}")

    response = await authenticated_client.get(
        "/posts",
        params={"page_number": 1, "page_size": 10},
    )

    assert response.status_code == 200

    data = response.json()
    assert all(item["id"] != post_id for item in data["items"])


async def test_delete_other_users_post_forbidden(
    client: AsyncClient,
    test_user: User,
    second_user: User,
    test_category,
) -> None:
    TEST_USER_EMAIL = "posts@example.com"
    TEST_USER_PASSWORD = "password123"
    SECOND_USER_EMAIL = "second@example.com"
    SECOND_USER_PASSWORD = "password123"

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

    response = await client.delete(f"/posts/{post_id}")
    assert response.status_code == 403
