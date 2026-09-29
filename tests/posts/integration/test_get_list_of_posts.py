from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.category_model import Category


async def _create_post(
    client: AsyncClient,
    category_id: int,
    title: str,
    content: str = "Content",
) -> dict:
    response = await client.post(
        "/posts",
        data={
            "title": title,
            "content": content,
            "category_id": str(category_id),
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_get_posts_pagination(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    for i in range(3):
        await _create_post(
            authenticated_client,
            test_category.id,
            f"Post {i}",
        )

    response = await authenticated_client.get(
        "/posts",
        params={"page_number": 1, "page_size": 2},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["pages"] == 2


async def test_posts_page_size_limit(client: AsyncClient) -> None:
    response = await client.get(
        "/posts",
        params={"page_number": 1, "page_size": 51},
    )
    assert response.status_code == 422


async def test_filter_posts_by_category(
    authenticated_client: AsyncClient,
    db_session: AsyncSession,
    test_category,
) -> None:
    other = Category(name="Other Category")
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)

    await _create_post(
        authenticated_client,
        test_category.id,
        "First category post",
    )
    await _create_post(
        authenticated_client,
        other.id,
        "Second category post",
    )

    response = await authenticated_client.get(
        "/posts",
        params={
            "category_id": test_category.id,
            "page_number": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert all(
        item["category_id"] == test_category.id
        for item in data["items"]
    )


async def test_search_posts(
    authenticated_client: AsyncClient,
    test_category,
) -> None:
    await _create_post(
        authenticated_client,
        test_category.id,
        "How to choose a laptop",
        "Important information about choosing a laptop for work.",
    )
    await _create_post(
        authenticated_client,
        test_category.id,
        "Cooking recipes",
        "How to cook pasta.",
    )

    response = await authenticated_client.get(
        "/posts",
        params={
            "search": "laptop",
            "page_number": 1,
            "page_size": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "How to choose a laptop"
