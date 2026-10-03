from sqlalchemy import func, select
from includes.core.paginator import NewQueryPaginator
from includes.db.connection import active_secondary_db
from includes.db.models.secondary import Article, ArticleView
from includes.utils.arti import get_mini_article_json

class ArticleTrendingService:

    @staticmethod
    async def get_article_rank(article_id: int) -> int | None:
        db_session = await active_secondary_db()
        
        rank_column = (
            func.row_number()
            .over(
                order_by=(ArticleView.updated_at.desc(), ArticleView.view_count.desc())
            )
            .label("rank")
        )

        stmt = select(ArticleView.id, rank_column).order_by(
            ArticleView.updated_at.desc(), ArticleView.view_count.desc()
        )

        result = db_session.execute(stmt)

        for row in result:
            if row.id == article_id:
                return row.rank

        return None

    @staticmethod
    async def get_articles(*, limit=12, **more):
        db = await active_secondary_db()

        rank_column = (
            func.row_number()
            .over(
                order_by=(ArticleView.updated_at.desc(), ArticleView.view_count.desc())
            )
            .label("rank")
        )

        query = (
            select(Article, rank_column)
            .join(ArticleView, Article.id == ArticleView.id)
            .where(Article.status == "Publish", Article.parameter != 0)
            .order_by(ArticleView.updated_at.desc(), ArticleView.view_count.desc())
        )

        data = await NewQueryPaginator.paginate(
            types="query",
            query=query,
            model=Article,
            limit=limit,
            db=db,
            transform=lambda item: get_mini_article_json(item, excerpt=True),
            **more,
        )

        return data.records
