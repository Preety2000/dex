from sqlalchemy import func
from sqlalchemy.orm import declarative_base


from includes.core.config import (
    exam_database,
    main_database,
    secondary_database,
)
from includes.core.config import (
    BaseOwner,
    BaseSecondary,
    ExamDb,
)


class DatabaseRouter:
    """
    Routes database operations to the appropriate SQLAlchemy session
    based on the model's __database_key__ attribute.
    """

    MAIN_DB = "db_main"
    EXAM_DB = "db_exam"

    def __init__(self):
        self.main_session = None
        self.exam_session = None
        self.secondary_session = None
        self.secondary_db_name = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @staticmethod
    def _assign_database(base, database_key: str):
        """
        Assign a database key to all models registered with the given base.
        """
        for mapper in base.registry.mappers:
            mapper.class_.__database_key__ = database_key

    async def configure(self, secondary_db_name: str = "hindi"):
        """
        Configure the main and secondary database sessions.
        """
        self.secondary_db_name = secondary_db_name

        self._assign_database(BaseOwner, self.MAIN_DB)
        self._assign_database(BaseSecondary, secondary_db_name)

        with (
            main_database() as main_session,
            secondary_database(secondary_db_name) as secondary_session,
        ):
            self.main_session = main_session
            self.secondary_session = secondary_session

            return main_session, secondary_session

    async def configure_main(self):
        """
        Configure the main database session.
        """
        self._assign_database(BaseOwner, self.MAIN_DB)

        with main_database() as main_session:
            self.main_session = main_session
            return main_session

    async def configure_secondary(self, db_name: str = "hindi"):
        """
        Configure the secondary database session.
        """
        self.secondary_db_name = db_name
        self._assign_database(BaseSecondary, db_name)

        with secondary_database(db_name) as secondary_session:
            self.secondary_session = secondary_session
            return secondary_session

    async def configure_exam(self):
        """
        Configure the exam database session.
        """
        self._assign_database(ExamDb, self.EXAM_DB)

        with exam_database() as exam_session:
            self.exam_session = exam_session
            return exam_session

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_session(self, database_key: str):
        """
        Return the session associated with a database key.
        """
        session_map = {
            self.MAIN_DB: self.main_session,
            self.EXAM_DB: self.exam_session,
            self.secondary_db_name: self.secondary_session,
        }

        session = session_map.get(database_key)

        if session is None:
            raise ValueError(
                f"Database session is not initialized or unknown: " f"{database_key!r}"
            )

        return session

    def _get_model_session(self, model):
        """
        Resolve a model's database key and return its session.
        """
        database_key = getattr(model, "__database_key__", None)

        if database_key is None:
            raise ValueError(
                f"Model {model.__name__!r} has no __database_key__ configured."
            )

        return self._get_session(database_key)

    def _get_object_session(self, obj):
        """
        Resolve an object's model database key and return its session.
        """
        return self._get_model_session(type(obj))

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def query(self, model):
        """
        Create a query for the given model using its configured database.
        """
        session = self._get_model_session(model)
        return session.query(model)

    def get(self, model, *filters, **filter_by):
        """
        Return the first matching record for the given model.
        """
        query = self.query(model)

        if filters:
            query = query.filter(*filters)

        if filter_by:
            query = query.filter_by(**filter_by)

        return query.first()

    # ------------------------------------------------------------------
    # Persistence operations
    # ------------------------------------------------------------------

    def add(self, obj):
        """
        Add an object to its configured database session.
        """
        session = self._get_object_session(obj)
        session.add(obj)
        return obj

    def add_all(self, objects):
        """
        Add multiple objects to their respective database sessions.

        Objects belonging to different databases are grouped automatically.
        """
        if not objects:
            return []

        sessions = {}

        for obj in objects:
            database_key = getattr(type(obj), "__database_key__", None)

            if database_key is None:
                raise ValueError(
                    f"Model {type(obj).__name__!r} has no "
                    f"__database_key__ configured."
                )

            if database_key not in sessions:
                sessions[database_key] = self._get_session(database_key)

            sessions[database_key].add(obj)

        return objects

    def count(self, model, column=None):
        session = self._get_model_session(model)

        if column is None:
            column = getattr(model, "id", None)

        if column is None:
            return session.query(func.count()).select_from(model).scalar()

        return session.query(func.count(column)).scalar()

    def delete(self, obj):
        """
        Delete an object from its configured database session.
        """
        session = self._get_object_session(obj)
        session.delete(obj)
        return obj

    def refresh(self, obj):
        """
        Refresh an object from its configured database.
        """
        session = self._get_object_session(obj)
        return session.refresh(obj)

    def flush(self):
        """
        Flush all initialized database sessions.
        """
        for session in self._sessions():
            session.flush()

    # ------------------------------------------------------------------
    # Transaction management
    # ------------------------------------------------------------------

    def commit(self):
        """
        Commit all initialized database sessions.

        If any commit fails, all initialized sessions are rolled back.
        """
        sessions = self._sessions()

        if not sessions:
            return

        try:
            for session in sessions:
                session.commit()
        except Exception as exc:
            self._rollback_all()
            raise RuntimeError("Database commit failed.") from exc

    def rollback(self):
        """
        Roll back all initialized database sessions.
        """
        errors = []

        for name, session in self._named_sessions():
            try:
                session.rollback()
            except Exception as exc:
                errors.append(f"{name}: {exc}")

        if errors:
            raise RuntimeError(f"Database rollback failed: {'; '.join(errors)}")

    def _rollback_all(self):
        """
        Internal rollback helper used after a failed commit.
        """
        for session in self._sessions():
            try:
                session.rollback()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _named_sessions(self):
        """
        Yield initialized sessions with their names.
        """
        sessions = (
            ("main_session", self.main_session),
            ("exam_session", self.exam_session),
            ("secondary_session", self.secondary_session),
        )

        for name, session in sessions:
            if session is not None:
                yield name, session

    def _sessions(self):
        """
        Return all initialized database sessions.
        """
        return [session for _, session in self._named_sessions()]

    def is_initialized(self):
        """
        Check whether the main and secondary sessions are initialized.
        """
        return self.main_session is not None and self.secondary_session is not None

    def close(self):
        """
        Close all initialized database sessions and reset the router state.
        """
        errors = []

        for name, session in self._named_sessions():
            try:
                session.close()
            except Exception as exc:
                errors.append(f"{name}: {exc}")

        self.main_session = None
        self.exam_session = None
        self.secondary_session = None
        self.secondary_db_name = None

        if errors:
            raise RuntimeError(
                f"Failed to close database sessions: {'; '.join(errors)}"
            )


db = DatabaseRouter()


async def active_exam_db():
    """Active exam database"""

    if db.exam_session is None:
        return await db.configure_exam()

    return db.exam_session


async def active_primary_db():
    """Active primary database"""

    if db.main_session is None:
        return await db.configure_main()

    return db.main_session


async def active_secondary_db():
    """Active primary database"""

    if db.secondary_session is None:
        return await db.configure_secondary()

    return db.secondary_session


async def get_contry():
    return "IND"
