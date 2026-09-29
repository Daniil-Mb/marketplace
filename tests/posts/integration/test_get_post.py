from httpx import AsyncClient


async def test_get_post(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    create = await authenticated_client.post(
        "/posts",
        data={
            "title": "Test post",
            "content": "Test content",
            "category_id": str(test_category.id),
        },
    )
    assert create.status_code == 201

    post_id = create.json()["id"]

    response = await authenticated_client.get(f"/posts/{post_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Test post"


async def test_get_missing_post(client: AsyncClient) -> None:
    response = await client.get(
        "/posts/00000000-0000-0000-0000-000000000000",
    )
    assert response.status_code == 404
