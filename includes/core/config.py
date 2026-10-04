from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from includes.core.globals.entry import app_context
from includes.database.models.db_exam import ExamDb
from includes.database.models.owner import BaseOwner
from includes.database.models.secondary import BaseSecondary

from includes.database.dir import (
    EXAM_DB_URL,
    MAIN_DB_URL,
    SECONDARY_DB_URLS,
)


# SQLAlchemy SESSION FACTORY
def create_session_factory(db_url: str, base):
    """
    Create SQLAlchemy engine and scoped session factory.
    Supports both SQLite and PostgreSQL.
    """

    is_sqlite = db_url.startswith("sqlite")

    if is_sqlite:
        engine = create_engine(
            db_url,
            connect_args={
                "check_same_thread": False,
            },
            pool_pre_ping=True,
        )

    else:
        engine = create_engine(
            db_url,
            pool_size=50,
            max_overflow=100,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    # Create tables automatically
    base.metadata.create_all(bind=engine)

    Session = scoped_session(
        sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )
    )

    return engine, Session


# MAIN DATABASE
main_engine, MainSession = create_session_factory(
    MAIN_DB_URL,
    BaseOwner,
)


# EXAM DATABASE
exam_engine, ExamSession = create_session_factory(
    EXAM_DB_URL,
    ExamDb,
)


# SECONDARY DATABASES
SecondarySessionList: dict[str, scoped_session] = {}

for db_key, db_url in SECONDARY_DB_URLS.items():

    engine, Session = create_session_factory(
        db_url,
        BaseSecondary,
    )

    SecondarySessionList[db_key] = Session


# DATABASE CONTEXT MANAGERS
@contextmanager
def main_database():
    """Main database session."""

    session = MainSession()

    try:
        yield session
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[Main DB Error] {e}")
        raise

    finally:
        session.close()


@contextmanager
def exam_database():
    """Exam database session."""

    session = ExamSession()

    try:
        yield session
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[Exam DB Error] {e}")
        raise

    finally:
        session.close()


@contextmanager
def secondary_database(db_key: str = app_context.db_key):
    """Secondary database session."""

    factory = SecondarySessionList.get(db_key)

    if not factory:
        raise ValueError(f"[Secondary DB Error] " f"No session factory for '{db_key}'")

    session = factory()

    try:
        yield session
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"[{db_key.upper()} DB Error] {e}")
        raise

    finally:
        session.close()


# LOCATION MODEL
class Location(BaseModel):

    # GPS
    latitude: float
    longitude: float

    # GPS metadata
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: Optional[int] = None

    # IP location
    ip: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal: Optional[str] = None
    timezone: Optional[str] = None
    org: Optional[str] = None

    # Misc
    source: Optional[str] = None
    device: Optional[str] = None


async def receive_location(location: Location):
    return {
        "message": "Location data received successfully!",
        "data": location,
    }


# SECURITY / COOKIE
MASTER_KEY = "qh5DB6lIEAkPk48e7KwVEJOkcQVAngkuy8_5O8y2tGu0tPyo2fulAbhaRGjyIMWzxY"


# APPLICATION SETTINGS
class Settings(BaseSettings):

    APP_NAME: str = "PhonePe FastAPI Payment"

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    # Optional because application is currently using SQLite
    # above. If DATABASE_URL is provided in Railway/.env,
    # it will still be available.
    DATABASE_URL: Optional[str] = None

    # --------------------------------------------------------
    # PhonePe
    # --------------------------------------------------------

    PHONEPE_ENV: str = "SANDBOX"

    PHONEPE_CLIENT_ID: Optional[str] = None
    PHONEPE_CLIENT_SECRET: Optional[str] = None
    PHONEPE_CLIENT_VERSION: Optional[str] = None

    # --------------------------------------------------------
    # URLs
    # --------------------------------------------------------

    FRONTEND_URL: Optional[str] = None
    BACKEND_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # --------------------------------------------------------
    # PhonePe Auth URL
    # --------------------------------------------------------

    @property
    def phonepe_auth_url(self) -> str:

        if self.PHONEPE_ENV.upper() == "PRODUCTION":
            return "https://api.phonepe.com/" "apis/identity-manager/v1/oauth/token"

        return "https://api-preprod.phonepe.com/" "apis/pg-sandbox/v1/oauth/token"

    # --------------------------------------------------------
    # PhonePe Base URL
    # --------------------------------------------------------

    @property
    def phonepe_base_url(self) -> str:

        if self.PHONEPE_ENV.upper() == "PRODUCTION":
            return "https://api.phonepe.com/apis/pg"

        return "https://api-preprod.phonepe.com/apis/pg-sandbox"


# GLOBAL SETTINGS INSTANCE

settings = Settings()
