from httpx import AsyncClient


async def test_create_post_without_image(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    response = await authenticated_client.post(
        "/posts",
        data={
            "title": "How to choose a product",
            "content": "Useful information about choosing products.",
            "category_id": str(test_category.id),
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "How to choose a product"
    assert data["content"] == "Useful information about choosing products."
    assert data["category_id"] == test_category.id
    assert "id" in data
    assert data["image_url"] is None


async def test_create_post_with_image(
    authenticated_client: AsyncClient,
    test_category,
    mock_file_service,
) -> None:
    response = await authenticated_client.post(
        "/posts",
        data={
            "title": "Post with image",
            "content": "Content",
            "category_id": str(test_category.id),
        },
        files={
            "image": ("test.jpg", b"fake-image-bytes", "image/jpeg"),
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["image_url"] is not None
    mock_file_service.upload_image.assert_awaited_once()


async def test_create_post_without_auth(
    client: AsyncClient,
    test_category,
) -> None:
    response = await client.post(
        "/posts",
        data={
            "title": "No auth",
            "content": "Content",
            "category_id": str(test_category.id),
        },
    )
    assert response.status_code == 401


async def test_create_post_unknown_category(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.post(
        "/posts",
        data={
            "title": "Title",
            "content": "Content",
            "category_id": "999999",
        },
    )
    assert response.status_code == 404
