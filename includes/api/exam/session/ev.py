import asyncio
from collections import deque

from includes.db.models.utils import TimeStamp

STUDENT_LIVE_IN_EXAME = {}

EVENT_TTL = 86400000  # 24 hours
# CLEANUP_INTERVAL = 240  # 4 min
CLEANUP_INTERVAL = 5  # 4 min
MAX_EVENTS_PER_EXAM = 5000  # safety cap (optional)

exam_request_session = {}


class ExamEventManager:

    # INIT SESSION
    @staticmethod
    async def start_exam_session(exam_id: int):
        return exam_request_session.setdefault(
            int(exam_id),
            {"event": deque(), "student_status": {}, "time": TimeStamp.now_timestamp()},
        )

    # PUSH EVENT
    @staticmethod
    async def push_exam_event(exam_id: int, event):
        session = exam_request_session.get(int(exam_id))

        print("________push_exam_event edite option")

        if not session:
            return

        events = session["event"]
        events.append((TimeStamp.now_timestamp(), event))

        # memory safety cap
        if len(events) > MAX_EVENTS_PER_EXAM:
            events.popleft()

    # FETCH EVENT (with cleanup)
    @staticmethod
    async def fetch_next_exam_event(exam_id: int):
        # print(f"\033[1;96m{exam_id, exam_request_session}\033[0m")

        session = exam_request_session.get(int(exam_id))
        if not session:
            return None

        now = TimeStamp.now_timestamp()
        session["time"] = now

        events = session["event"]
        while events and (now - events[0][0] > EVENT_TTL):
            events.popleft()

        if events:
            _, event = events.popleft()
            return event

        return None

    # UPDATE STUDENT STATUS
    @staticmethod
    async def update_student_status(exam_id: int, status_id):
        session = exam_request_session.get(int(exam_id))
        if not session:
            return

        session["student_status"][status_id] = TimeStamp.now_timestamp()

    # GROUP STATUS (recent/expired)
    @staticmethod
    async def get_student_status_groups(exam_id: int):
        session = exam_request_session.get(int(exam_id))
        if not session:
            return [], []

        cutoff = TimeStamp.now_timestamp() - EVENT_TTL

        recent, expired = [], []

        for status_id, ts in session["student_status"].items():
            if ts > cutoff:
                recent.append((status_id, ts))
            else:
                expired.append((status_id, ts))

        return recent, expired

    @staticmethod
    async def get_availability(exam_id: int, defreant=EVENT_TTL) -> bool:
        session = exam_request_session.get(int(exam_id))
        if not session:
            return True

        return (TimeStamp.now_timestamp() - session.get("time", 0)) > defreant
