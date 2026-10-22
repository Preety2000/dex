import json
import ast
from datetime import date, datetime

from includes.src.request import Request
from includes.api.exam.student import RecordType, Student
from includes.api.exam.results.results_conducted import IS_RESULTS
from includes.api.exam.results.results_practice import SELF_RESULTS
from includes.core.globals.route_context import Route


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        return super(CustomJSONEncoder, self).default(obj)


class Results:

    @staticmethod
    async def index(request:Request):
        source, code = (
            (request.state.roote.action, RecordType.STUDENT)
            if (request.state.roote.entity and request.state.roote.action)
            else (request.state.roote.entity, RecordType.INVIGILATOR)
        )

        record = await Student.get_by_exam_key(source, code)
        request.state.response["record"] = record
        return "widget/results_index"
