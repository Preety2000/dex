from includes.admin.api.schemas.category import AdminApiCategory
from includes.admin.api.schemas.practice import AdminApiMCQ
from includes.utils.utils import get_post_value


class AdminInsurt:

    @classmethod
    async def exiute(cls):
        root = await get_post_value("root", None)
        datatype = await get_post_value("datatype", None)

        if root is None:
            return {"error": "6a8473f9-73d4-83ea-ba81-6a76a0d9fd82"}

        if root == "cot":
            responce = await AdminApiCategory.insert()
            responce["datatype"] = datatype
            return responce

        if root == "practice":
            responce = await AdminApiMCQ.insert()
            responce["datatype"] = datatype
            return responce

        return {"root": root}
