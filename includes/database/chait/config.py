import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from includes.database.chait.base import BaseTeachers

# Get the current directory
current_dir = os.getcwd()

# Define the folder path and ensure it exists
FolderPath = os.path.join(current_dir, "database")
os.makedirs(FolderPath, exist_ok=True)

# Context manager for dynamic SQLite DB access
@contextmanager
def AsyncSQLiteMainDatabase():
    """
    Context manager to create and use a SQLite database session dynamically
    """

    # Full path to the SQLite database file
    dbFilePath = os.path.join(FolderPath, "DBTS_002.sqlite3")

    # SQLite DB URL
    db_url = f"sqlite:///{dbFilePath}"

    # Create engine (SQLite does not use connection pooling)
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )

    # Create tables defined in BaseTeachers if they don't exist
    BaseTeachers.metadata.create_all(bind=engine)

    # Create session factory
    SessionFactory = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

    # Use the session
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(f"[SQLite DB Error] {e}")
        session.rollback()
    finally:
        session.close()
        SessionFactory.remove()
