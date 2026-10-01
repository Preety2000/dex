from includes.schemas.router_schema import DynamicURLRoute


class ClassMedia:

    @classmethod
    async def index(cls, roots: DynamicURLRoute):
        return "admin/media"
