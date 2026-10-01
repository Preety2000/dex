from includes.api.exam.student import Student
from includes.api.exam.socket.teacher import requestRoute
from includes.utils.utils import get_post_value


class ReqRoute:
    def __init__(self, roots, exam_id):
        self.roots = roots
        self.exam_id = exam_id

    async def execute_authorized(self, payload, use_filter):
        if self.roots == "studentReqs":
            offset, limit = payload

            return await requestRoute.studentReqs(
                self.exam_id, [offset, limit], use_filter
            )

        if self.roots == "reqApprAct":
            return await requestRoute.studentReqsAptAll(self.exam_id, payload)

        if self.roots == "stuReqsBlk":
            return await requestRoute.blocked_student_list(
                payload=payload, exam_id=self.exam_id, use_filter=use_filter
            )

        if self.roots == "stuReqsRemv":
            return await requestRoute.remove_student_list(
                payload=payload, exam_id=self.exam_id, use_filter=use_filter
            )

        print("execute_authorized")

    async def execute_public(self, payload):
        if self.roots == "practiceDelete":
            key, roll_no = payload
            return await Student.delete(key, roll_no)

        print("execute_public")
        return {}

    async def execute(self, has_access):
        print("has_access", has_access)
        use_filter = await get_post_value("useFilter")
        payload = await get_post_value("payload")
        if has_access:
            return await self.execute_authorized(payload, use_filter)

        return await self.execute_public(payload)
