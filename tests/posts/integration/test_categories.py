from httpx import AsyncClient


async def test_create_category(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.post(
        "/categories",
        json={"name": "Electronics"},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Electronics"
    assert "id" in data


async def test_get_categories(
    client: AsyncClient,
    test_category,
) -> None:
    response = await client.get("/categories")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert any(c["id"] == test_category.id for c in data)


async def test_create_category_without_auth(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/categories",
        json={"name": "Unauthorized"},
    )
    assert response.status_code == 401


async def test_create_duplicate_category(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    response = await authenticated_client.post(
        "/categories",
        json={"name": test_category.name},
    )
    assert response.status_code == 409
