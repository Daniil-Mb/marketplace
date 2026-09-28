from sqlalchemy import Select, func

from src.core.database.models.post_model import Post


class PostFilterMixin:
    def apply_category_filter(
        self,
        query: Select,
        category_id: int | None,
    ) -> Select:
        if category_id is None:
            return query

        return query.where(
            Post.category_id == category_id,
        )

    def apply_search_filter(
        self,
        query: Select,
        search: str | None,
    ) -> Select:
        if not search:
            return query

        search_query = func.websearch_to_tsquery(
            "russian",
            search,
        )

        return query.where(
            Post.search_vector.op("@@")(search_query),
        )

    def apply_search_order(
        self,
        query: Select,
        search: str | None,
    ) -> Select:
        if not search:
            return query.order_by(
                Post.created_at.desc(),
            )

        search_query = func.websearch_to_tsquery(
            "russian",
            search,
        )

        return query.order_by(
            func.ts_rank(
                Post.search_vector,
                search_query,
            ).desc(),
            Post.created_at.desc(),
        )
