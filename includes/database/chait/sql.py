from contextlib import contextmanager
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

current_dir = os.getcwd()
default_folder_path = os.path.join(current_dir, "database")


class Class:
    pass


# class LocalDB:
#     def __init__(self, db_file, base, folder=None):
#         # Use a local variable to handle custom folder paths
#         folder_path = default_folder_path
#         if folder:
#             folder_path = os.path.join(default_folder_path, folder)

#         # Ensure directory exists
#         os.makedirs(folder_path, exist_ok=True)

#         # Construct full path to DB file
#         full_path = os.path.join(folder_path, db_file)

#         # Create SQLAlchemy engine and session
#         self.engine = create_engine(f"sqlite:///{full_path}", echo=False)

#         self.Session = scoped_session(
#             sessionmaker(
#                 bind=self.engine,
#                 autocommit=False,
#                 autoflush=False
#             )
#         )
#         # self.session = self.Session()

#         # Create all tables defined using Base
#         base.metadata.create_all(self.engine)

#     @contextmanager
#     def session_scope(self):
#         """Provide a transactional scope around a series of operations."""
#         session = self.Session()
#         try:
#             yield session
#             session.commit()
#         except Exception as e:
#             print(f"[LocalDB Error] {e}")
#             session.rollback()
#             raise
#         finally:
#             session.close()


#     def initialize_tables(self, tables, container=None):
#         if not isinstance(tables, list):
#             tables = [tables]

#         if containeris None:
#             container= Class()

#         for table in tables:
#             if not hasattr(table, "__tablename__"):
#                 continue

#             table_name = table.__tablename__

#             setattr(self, table_name, self.session.query(table))
#             setattr(container, table_name, table)

#         return container


import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TableRegistry:
    pass


class LocalDB:
    def __init__(self, db_file, base, folder=None):
        folder_path = (
            os.path.join(default_folder_path, folder) if folder else default_folder_path
        )

        os.makedirs(folder_path, exist_ok=True)
        db_path = os.path.join(folder_path, db_file)

        self.engine = create_engine(
            f"sqlite:///{db_path}", echo=False, pool_pre_ping=True
        )

        base.metadata.create_all(self.engine)
        self.Session = scoped_session(
            sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        )

        self.session = self.Session()

    @contextmanager
    def session_scope(self):
        session = self.Session()

        try:
            yield session
            session.commit()

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    async def register_tables(self, tables, registry=None):

        if not isinstance(tables, (list, tuple)):
            tables = [tables]

        if registry is None:
            registry = TableRegistry()

        for table in tables:

            if not hasattr(table, "__tablename__"):
                continue

            setattr(self, table.__tablename__, self.session.query(table))

            setattr(registry, table.__tablename__, table)

        return registry

    def close(self):
        self.engine.dispose()
