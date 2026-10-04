from includes.database.models.secondary import Books


class ClassBooks:

    async def index(self, subresource, detail):
        print("create function")
        return "widget/books"
