from includes.core.globals.entry import app_context
from includes.db.models.secondary import Books
from includes.schemas.subject import ClassSubject


class ClassBooks:
    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function

    def json(self, query):
        if not query:
            return None
        dictionary = {
            "id": query.id,
            "slug": query.slug,
            "name": query.name,
            "excerpt": query.excerpt,
            "subject": query.subject,
            "writer": query.writer,
            "image_src": query.image_src,
        }

        coverti = query.name.split(" ")

        cover = app_context.svg_lists["bookcover"]
        strn = ""
        count = 3000
        for item in coverti:
            strn += f'<text x="450" y="{count}"  class="fil2o fnt0b">{item}</text>'
            count = count + 1000

        cover = cover.replace("</$text>", strn)

        dictionary.update({"cover": cover})
        for [name, value] in (ClassSubject.get(query.subject) or {}).items():
            dictionary.update({f"subject_{name}": value})

        return dictionary

    def getList(self, limit):
        all_query = self.function.filterData(
            app_context.db.query(Books), Books, limit=limit
        )
        return [self.json(item) for item in all_query]

    def get(self, query=None, quet=None):
        # Try filtering by id, slug, or title, returning the first match
        query = (
            app_context.db.query(Books)
            .filter((Books.id == query) | (Books.slug == query))
            .first()
        )

        return self.json(query) if quet is None else query

    def index(self, subresource, detail):
        app_context.response["data_querys"] = self.getList(12)
        return "widget/books"
