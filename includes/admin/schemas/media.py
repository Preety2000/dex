from includes.core.globals.route_context import Route


class ClassMedia:

    @classmethod
    async def index(cls, roots: Route):
        return "admin/media"
