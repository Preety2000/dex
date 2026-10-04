import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from langdetect import DetectorFactory

from sqlalchemy import select, or_, desc

from includes.core.paginator import NewQueryPaginator
from includes.database.models.owner import Subject
from includes.database.models.utils import TimeStamp
from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import (
    format_view_count,
)
from includes.core.metadata import MetaData
from includes.core.pagination import Pagination
from includes.database.connection import db
from includes.database.models.secondary import (
    Article,
    ArticleMetadata,
    QuizQuestion,
    QuizRelationships,
    Suggestion,
    Terms,
    TermsRelationship,
)
from includes.schemas.terms import get_terms_json
from includes.utils.arti import get_mini_article_json
from includes.utils.utils import get_post_value
from includes.schemas.word.hindi_stopwords import HINDI_STOP_WORDS
from includes.schemas.word.english_stopwords import ENGLISH_STOP_WORDS

# भाषा की पहचान के लिए सीड
DetectorFactory.seed = 0


# OpenAI API
OPENAI_URL = "https://api.openai.com/v1/completions"



def postsmetatags_json(query):
    if not query:
        return None

    # Subject
    subject_stmt = select(Subject).where(Subject.id == query.subject)

    subject_obj = db.execute(subject_stmt).scalar_one_or_none()

    subjects = app_context.subject.json(subject_obj) if subject_obj else None

    # Safe tag filtering and mapping
    tags_group = query.tags_group or []

    suggestion_ints = [int(x) for x in tags_group if str(x).isdigit()]

    if suggestion_ints:

        suggestion_stmt = select(Suggestion).where(Suggestion.id.in_(suggestion_ints))

        suggestions = db.execute(suggestion_stmt).scalars().all()

        suggestion_data = [
            {
                "tag": item.tags,
                "used": item.most_used,
            }
            for item in suggestions
        ]

    else:
        suggestion_data = []

    return {
        "id": query.id,
        "subject": subjects,
        "excerpt": query.excerpt,
        "secret_key": query.secret_key,
        "tags": suggestion_data,
    }


class Search:

    def __init__(self, request):
        self.count = 0
        self.request = request
        self.function = app_context.function
        self.keywords = []
        self.search_term_array_vars = []
        self.category_type = str
        self.category_arry = True
        self.category_data = None

        parsed_url = urlparse(str(request.url))

        self.host_url = f"{parsed_url.scheme}://" f"{parsed_url.netloc}/"

    def search_term_array(self, search_term):
        search_term_clean = re.sub(
            r"[।.,?]",
            "",
            search_term,
        )

        words = search_term_clean.split()

        filtered_words = [
            word
            for word in words
            if (word not in HINDI_STOP_WORDS and word not in ENGLISH_STOP_WORDS)
        ]

        search_term_array_1 = [x for x in words if x]

        search_term_array_2 = [x for x in filtered_words if len(x) > 2]

        return (
            search_term_array_1,
            search_term_array_2,
        )

    def article_property(self, query):

        # Terms
        terms_stmt = select(Terms).where(Terms.id == query.parameter)

        terms = db.execute(terms_stmt).scalar_one_or_none()

        # Type
        type_stmt = select(Terms).where(Terms.id == query.type)

        query.types = db.execute(type_stmt).scalar_one_or_none()

        if terms:
            query.uri = f"{terms.slug}/{query.slug}" if terms.id != 0 else query.slug

            query.terms = terms
            query.resource = terms.id
            query.parameters = terms
            query.resourcetype = terms.slug

        else:
            query.uri = f"/{query.slug}"
            query.terms = None
            query.resource = None
            query.parameters = None
            query.resourcetype = None

        # Article categories
        category_stmt = (
            select(Terms)
            .join(
                TermsRelationship,
                TermsRelationship.terms_id == Terms.id,
            )
            .where(TermsRelationship.article_id == query.id)
        )

        query.category = db.execute(category_stmt).scalars()

        # Article metadata
        metadata_stmt = select(ArticleMetadata).where(ArticleMetadata.id == query.id)

        terms_relationship = db.execute(metadata_stmt).scalar_one_or_none()

        if terms_relationship:

            query.meta_data = terms_relationship

            subject_stmt = select(Subject).where(
                Subject.id == terms_relationship.subject_id
            )

            subject_query = db.execute(subject_stmt).scalar_one_or_none()

            query.subjects = subject_query

            query.subject = subject_query.slug if subject_query else None

        else:

            type_meta = type(
                "ArticleMetadata",
                (),
                {},
            )

            query.meta_data = type_meta()
            query.meta_data.id = query.id
            query.meta_data.excerpt = ""
            query.meta_data.tags_group = ""
            query.subject = None
            query.subjects = None

        # Suggestions
        if getattr(
            query.meta_data,
            "tags_group",
            None,
        ):

            tags_group = [
                int(x) for x in query.meta_data.tags_group if str(x).isdigit()
            ]

            if tags_group:

                suggestion_stmt = select(Suggestion).where(
                    Suggestion.id.in_(tags_group)
                )

                query.suggestion = db.execute(suggestion_stmt).scalars().all()

            else:
                query.suggestion = None

        else:
            query.suggestion = None

        return query

    def suggestion_property(self, query):

        article_stmt = select(Article).where(Article.id == query.query_id)

        query.article = db.execute(article_stmt).scalars()

        return query

    def subject_json(self, query):
        if not query:
            return None

        return {
            "id": query.id,
            "name": query.name,
            "slug": query.slug,
            "used": query.used,
        }

    def find_best_match(
        self,
        matching_words,
        content,
    ):
        if not matching_words or not content:
            return ""

        matching_pattern = (
            r"\b(?:" + "|".join(re.escape(word) for word in matching_words) + r")\b"
        )

        pattern = re.compile(
            matching_pattern,
            re.IGNORECASE,
        )

        best_match = ""
        max_match_count = 0

        for sentence in content:
            matches = pattern.findall(sentence)

            match_count = len(matches)

            if match_count > max_match_count:
                max_match_count = match_count
                best_match = sentence

        return best_match

    def find_best_match_and_highlight(
        self,
        matching_words,
        content,
    ):
        if not matching_words or not content:
            return ""

        matching_pattern = (
            r"\b(?:" + "|".join(re.escape(word) for word in matching_words) + r")\b"
        )

        pattern = re.compile(
            matching_pattern,
            re.IGNORECASE,
        )

        best_match = ""
        max_match_count = 0

        for sentence in content:

            matches = pattern.findall(sentence)

            match_count = len(matches)

            if match_count > max_match_count:
                max_match_count = match_count
                best_match = sentence

        if best_match:

            matching_set = set(matching_words)

            words = best_match.split()

            highlighted = [
                (
                    f"<b>{word}</b>"
                    if word.replace(
                        "\n",
                        "",
                    )
                    in matching_set
                    else word
                )
                for word in words
            ]

            return " ".join(highlighted)

        return best_match

    def get_best_matching_content_with_all_words(
        self,
        content,
        matching_words,
    ):
        return [
            item for item in content if all(word in item for word in matching_words)
        ]

    async def article_json(self, query):
        if not query:
            return None

        query1 = await get_mini_article_json(
            query,
            excerpt=True,
            trending=True,
            category=True,
        )

        soup = BeautifulSoup(
            query.content or "",
            "html.parser",
        )

        def excerpt_getter(excerpt_text):

            parts = excerpt_text.split("।")

            if query1.get("excerpt"):
                parts.append(query1.get("excerpt"))

            qarts = [item for item in parts if len(item) >= 100]

            excerpt = self.find_best_match_and_highlight(
                self.search_term_array_vars,
                qarts,
            )

            matched_fallback = self.find_best_match_and_highlight(
                self.search_term_array_vars,
                parts,
            )

            if len(matched_fallback) <= 0 and qarts:
                return qarts[0]

            return excerpt

        excerpt = excerpt_getter(soup.get_text())

        if excerpt:
            query1["excerpt"] = excerpt

        return query1

    def mcqs_property(self, query):
        if not query:
            return None

        # Categories
        category_stmt = (
            select(Terms)
            .join(
                QuizRelationships,
                QuizRelationships.terms_id == Terms.id,
            )
            .where(QuizRelationships.quiz_id == query.id)
        )

        query.category = db.execute(category_stmt).scalars()

        # Subject
        subject_stmt = select(Subject).where(Subject.id == query.subject_id)

        query.subjects = db.execute(subject_stmt).scalar_one_or_none()

        # First relationship
        relationship_stmt = (
            select(QuizRelationships)
            .where(QuizRelationships.quiz_id == query.id)
            .limit(1)
        )

        rel = db.execute(relationship_stmt).scalar_one_or_none()

        query.category_id = rel.terms_id if rel else None

        return query

    def mcqs_json(self, query, quet=None):

        query = self.mcqs_property(query)

        if not query:
            return None

        category = []

        incorrect_answers = query.incorrect_answers or []

        # Relationships
        relationship_stmt = select(QuizRelationships).where(
            QuizRelationships.quiz_id == query.id
        )

        relationships = db.execute(relationship_stmt).scalars().all()

        for x in relationships:

            terms_stmt = select(Terms).where(Terms.id == x.terms_id)

            terms = db.execute(terms_stmt).scalar_one_or_none()

            categor = (
                x.terms_id
                if self.category_type == int
                else (terms.name if terms else "")
            )

            category.append(categor)

        category_data = quet or self.category_data

        if self.category_arry != str:

            category_items = (
                db.execute(
                    select(Terms)
                    .join(
                        QuizRelationships,
                        QuizRelationships.terms_id == Terms.id,
                    )
                    .where(QuizRelationships.quiz_id == query.id)
                )
                .scalars()
                .all()
            )

            if isinstance(
                category_data,
                list,
            ):

                category = [
                    {qt: item.get(qt) for qt in category_data}
                    for item in map(
                        lambda i: get_terms_json(i),
                        category_items,
                    )
                ]

            else:

                category = [get_terms_json(item) for item in category_items]

        sno = getattr(
            query,
            "sno",
            1,
        )

        # First category
        first_category_stmt = (
            select(Terms)
            .join(
                QuizRelationships,
                QuizRelationships.terms_id == Terms.id,
            )
            .where(QuizRelationships.quiz_id == query.id)
            .limit(1)
        )

        first_category = db.execute(first_category_stmt).scalar_one_or_none()

        options = list(incorrect_answers)

        if query.correct_answer:
            options.append(query.correct_answer)

        options = sorted(options)

        subject_name = query.subjects.name if query.subjects else ""

        dictionary = {
            "id": query.id,
            "question": query.question,
            "excerpt": query.excerpt,
            "correct_answer": query.correct_answer,
            "sno": sno,
            "subject": subject_name,
            "status": query.status,
            "options": options,
            "category": first_category,
            "timestamp": query.timestamp,
        }

        dictionary.update(
            {
                "date": TimeStamp.format_datetime(dictionary.get("timestamp")),
                "views": format_view_count(dictionary.get("views")),
            }
        )

        # Existing custom repository logic
        if isinstance(
            category_data,
            dict,
        ):

            cat_obj = db.category.get(
                category_data.get("id"),
                True,
            )

            if cat_obj:

                next_mcq = (
                    cat_obj.practice.filter(QuizQuestion.question > query.question)
                    .order_by(QuizQuestion.question.asc())
                    .first()
                )

                prev_mcq = (
                    cat_obj.practice.filter(QuizQuestion.question < query.question)
                    .order_by(QuizQuestion.question.desc())
                    .first()
                )

                if next_mcq:
                    dictionary.update(
                        {
                            "next_id": next_mcq.id,
                            "next_question": (next_mcq.question),
                        }
                    )

                if prev_mcq:
                    dictionary.update(
                        {
                            "prev_id": prev_mcq.id,
                            "prev_question": (prev_mcq.question),
                        }
                    )

        return dictionary

    def mcqs_search(
        self,
        search_term,
        question_limit,
    ):
        self.search_term = search_term
        self.question_limit = question_limit

        search_term_array = [x for x in search_term.split(" ") if len(x) > 3]

        conditions = [QuizQuestion.question.ilike(f"%{self.search_term}%")]

        for term in search_term_array:
            conditions.append(QuizQuestion.question.ilike(f"%{term}%"))

        # SQLAlchemy 2.x SELECT
        quiz_stmt = select(QuizQuestion).where(or_(*conditions))

        limit_val = question_limit or 20

        quiz_stmt = quiz_stmt.limit(limit_val)

        quizquestion = db.execute(quiz_stmt).scalars().all()

        mcqs_result = []
        index = 0

        for item in quizquestion:

            if item.excerpt:

                mcqs_result.append(
                    self.mcqs_json(
                        item,
                        True,
                    )
                )

                index += 1

            if question_limit == index:
                break

        return mcqs_result

    async def index(self, root=None):

        configure_page(
            template="query/search",
            title="Search",
            suffix=True,
        )

        response2 = {"resource": "widget"}

        search_term = self.function.get_request_value("q")

        search_tag = self.function.get_request_value("tag")

        search_page_uri = f"{self.host_url}search"

        if search_term:

            configure_page(
                title=search_term,
                suffix=True,
            )

            response2["search_term"] = search_term

            (
                self.search_term_array_vars,
                search_term_array,
            ) = self.search_term_array(search_term)

            # -------------------------------------------------
            # Article search conditions
            # -------------------------------------------------

            search_conditions = [
                Article.title.ilike(f"%{search_term}%"),
                Article.content.ilike(f"%{search_term}%"),
            ]

            for term in search_term_array:
                search_conditions.append(Article.title.ilike(f"%{term}%"))

            # -------------------------------------------------
            # Suggestion matches
            # -------------------------------------------------

            suggestion_stmt = select(Suggestion).where(
                Suggestion.tags.ilike(f"%{search_term}%")
            )

            suggestions = db.execute(suggestion_stmt).scalars().all()

            suggestion_article_ids = [
                s.query_id
                for s in suggestions
                if getattr(
                    s,
                    "query_id",
                    None,
                )
            ]

            if suggestion_article_ids:

                search_conditions.append(Article.id.in_(suggestion_article_ids))

            # -------------------------------------------------
            # Terms matches
            # -------------------------------------------------

            terms_stmt = select(Terms).where(Terms.name.ilike(f"%{search_term}%"))

            matched_terms = db.execute(terms_stmt).scalars().all()

            if matched_terms:

                term_ids = [t.id for t in matched_terms]

                terms_relationship_stmt = select(TermsRelationship).where(
                    TermsRelationship.terms_id.in_(term_ids)
                )

                article_ids_from_terms = [
                    tr.article_id
                    for tr in (db.execute(terms_relationship_stmt).scalars().all())
                ]

                if article_ids_from_terms:

                    search_conditions.append(Article.id.in_(article_ids_from_terms))

            # -------------------------------------------------
            # Unified Article Query
            # -------------------------------------------------

            query = select(Article).where(or_(*search_conditions)).distinct()

            # Exact term
            exact_term_stmt = select(Terms).where(Terms.name == search_term).limit(1)

            terms = db.execute(exact_term_stmt).scalar_one_or_none()

            (
                response2["data_querys"],
                response2["paginator"],
                response2["results"],
            ) = await Pagination.get_paginate(
                query=query,
                limit=10,
                transform=lambda item: (self.article_json(item)),
            )

            response2["terms"] = get_terms_json(terms) if terms else None

            response2["suggestion"] = self.suggestion(search_term)

            response2["mcq_results"] = self.mcqs_search(
                search_term,
                4,
            )

            for suggt in response2["suggestion"]:
                self.keywords.append(suggt["name"])

            keywords = self.get_best_matching_content_with_all_words(
                self.keywords,
                self.search_term_array_vars,
            )

            response2["keywords"] = list(set(keywords))

            MetaData.template = "query/search_query"

            return response2

        if search_tag:

            category_stmt = select(Terms).where(Terms.name == search_tag).limit(1)

            category = db.execute(category_stmt).scalar_one_or_none()

            if category:

                articles = (
                    select(Article)
                    .join(
                        TermsRelationship,
                        TermsRelationship.article_id == Article.id,
                    )
                    .where(TermsRelationship.terms_id == category.id)
                )

                data = await NewQueryPaginator.paginate(
                    db=db,
                    types="query",
                    query=articles,
                    model=Article,
                    transform=lambda item: (self.article_json(item)),
                    limit=20,
                )

                response2["data_querys"] = data.records

            response2["page_type"] = "search"

            response2["search_term"] = search_tag

            response2["terms_query"] = get_terms_json(category) if category else None

            configure_page(
                template="query/tagged",
                title=search_tag,
                suffix=True,
            )

            return response2

        if self.request.url == search_page_uri:
            return response2

        MetaData.redirect_url = self.host_url + "search"

        return {}

    def suggestion(
        self,
        search_term,
        limit=10,
    ):
        suggestions = []

        suggestion_stmt = (
            select(Suggestion)
            .where(Suggestion.tags.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        suggestion_query = db.execute(suggestion_stmt).scalars().all()

        for item in suggestion_query:

            new_uri = item.tags.replace(
                " ",
                "+",
            )

            uri = f"{self.host_url}" f"search?q={new_uri}"

            if item.tags != search_term:

                suggestions.append(
                    {
                        "name": item.tags,
                        "url": uri,
                    }
                )

        return suggestions

    async def list(self):

        search_term_arrays = await get_post_value("q") or []

        l2 = []

        for search_term in search_term_arrays:

            (
                search_term_array1,
                search_term_array,
            ) = self.search_term_array(search_term)

            article_conditions = [Article.title.ilike(f"%{search_term}%")]

            suggestion_conditions = [Suggestion.tags.ilike(f"%{search_term}%")]

            for insex in search_term_array:

                insex_clean = insex.replace(",", "")

                article_conditions.append(Article.title.ilike(f"%{insex_clean}%"))

                suggestion_conditions.append(Suggestion.tags == insex_clean)

            # -------------------------------------------------
            # Matching suggestions
            # -------------------------------------------------

            suggestion_stmt = select(Suggestion).where(or_(*suggestion_conditions))

            matched_suggestions = db.execute(suggestion_stmt).scalars().all()

            matched_query_ids = [
                s.query_id
                for s in matched_suggestions
                if getattr(
                    s,
                    "query_id",
                    None,
                )
            ]

            if matched_query_ids:

                article_conditions.append(Article.id.in_(matched_query_ids))

            # -------------------------------------------------
            # Combined articles
            # -------------------------------------------------

            articles_stmt = select(Article).where(or_(*article_conditions)).distinct()

            combined_articles = db.execute(articles_stmt).scalars().all()

            lists = []

            for match in combined_articles:

                match = self.article_property(match)

                lists.append(
                    {
                        "uri": "/" + match.uri,
                        "title": match.title,
                    }
                )

            l2.append(
                [
                    search_term,
                    lists,
                ]
            )

        return l2
