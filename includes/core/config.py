from pathlib import Path
from typing import Optional, Dict
from pydantic import BaseModel
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session

from includes.core.globals.entry import app_context
from includes.db.models.db_exam import ExamDb
from includes.db.models.owner import BaseOwner
from includes.db.models.secondary import BaseSecondary


from typing import Dict
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from includes.core.globals.entry import app_context
from includes.db.models.db_exam import ExamDb
from includes.db.models.owner import BaseOwner
from includes.db.models.secondary import BaseSecondary

# Configuration

# PostgreSQL connection format:
# postgresql+psycopg://username:password@host:port/database

# MAIN_DB_URL = "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_vidya"

# EXAM_DB_URL = "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_exam"

# SECONDARY_DB_URLS = {
#     "hindi": "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_hindi"
# }


BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "sqlite"

# Folder automatically create
DB_DIR.mkdir(parents=True, exist_ok=True)

MAIN_DB_URL = f"sqlite:///{DB_DIR / 'db_vidya.db'}"

EXAM_DB_URL = f"sqlite:///{DB_DIR / 'db_exam.db'}"

SECONDARY_DB_URLS = {"hindi": f"sqlite:///{DB_DIR / 'db_hindi.db'}"}


# --- Session Factories ---
def create_session_factory(db_url: str, base):
    """Creates SQLAlchemy engine + scoped session factory."""

    # engine = create_engine(
    #     db_url,
    #     pool_size=50,
    #     max_overflow=100,
    #     pool_timeout=30,
    #     pool_recycle=1800,
    #     pool_pre_ping=True,
    # )

    # base.metadata.create_all(bind=engine)
    # Session = scoped_session(
    #     sessionmaker(bind=engine, autocommit=False, autoflush=False)
    # )

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

    # Create tables if they don't exist
    base.metadata.create_all(bind=engine)

    Session = scoped_session(
        sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
        )
    )

    return engine, Session


# Main DB Engine + Session
# Factories for your databases (assume these are properly defined)
main_engine, MainSession = create_session_factory(MAIN_DB_URL, BaseOwner)

# Exam DB Engine + Session
# Factories for your databases (assume these are properly defined)
exam_engine, ExamSession = create_session_factory(EXAM_DB_URL, ExamDb)


SecondarySessionList: Dict[str, sessionmaker] = {}
for db_key, db_url in SECONDARY_DB_URLS.items():

    # Factories for your databases (assume these are properly defined)
    engine, Session = create_session_factory(db_url, BaseSecondary)
    SecondarySessionList[db_key] = Session


# --- Utility Functions ---
@contextmanager
def main_database():
    """Context manager for main DB session."""

    session = MainSession()
    try:
        yield session

    except Exception as e:
        print(f"[Main DB Error] {e}")
        session.rollback()

    finally:
        session.close()


@contextmanager
def exam_database():
    """Context manager for main DB session."""
    session = ExamSession()

    try:
        yield session
    except Exception as e:
        print(f"[Exam DB Error] {e}")
        session.rollback()
    finally:
        session.close()


@contextmanager
def secondary_database(db_key: str = app_context.db_key):
    """Context manager for secondary DB sessions."""

    factory = SecondarySessionList.get(db_key)
    if not factory:
        print(f"[Secondary DB Error] No session factory for '{db_key}'")
        yield None
        return

    session = factory()
    try:
        yield session
    except Exception as e:
        print(f"[{db_key.upper()} DB Error] {e}")
        session.rollback()
    finally:
        session.close()


from pydantic import BaseModel
from typing import Optional


class Location(BaseModel):
    # Core GPS coordinates
    latitude: float
    longitude: float

    # Optional GPS metadata
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    altitudeAccuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: Optional[int] = None

    # IP-based location info (optional)
    ip: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal: Optional[str] = None
    timezone: Optional[str] = None
    org: Optional[str] = None

    # Misc
    source: Optional[str] = None  # "gps", "ip", "wifi", "manual", etc.
    device: Optional[str] = None  # Device type or name (optional)


async def receive_location(location: Location):
    return {"message": "Location data received successfully!", "data": location}


MASTER_KEY = "qh5DB6lIEAkPk48e7KwVEJOkcQVAngkuy8_5O8y2tGu0tPyo2fulAbhaRGjyIMWzxY"
DEFAULT_COOKIE = (
    "Em4FYvhv.0.0.qh5DB6lIEAkPk48e7KwVEJOkcQVAngkuy8_5O8y2tGu0tPyo2fulAbhaRGjyIMWzxY"
)


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "PhonePe FastAPI Payment"

    DATABASE_URL: str

    PHONEPE_ENV: str = "SANDBOX"

    PHONEPE_CLIENT_ID: str
    PHONEPE_CLIENT_SECRET: str
    PHONEPE_CLIENT_VERSION: str

    FRONTEND_URL: str
    BACKEND_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def phonepe_auth_url(self) -> str:

        if self.PHONEPE_ENV.upper() == "PRODUCTION":
            return "https://api.phonepe.com/" "apis/identity-manager/v1/oauth/token"

        return "https://api-preprod.phonepe.com/" "apis/pg-sandbox/v1/oauth/token"

    @property
    def phonepe_base_url(self) -> str:

        if self.PHONEPE_ENV.upper() == "PRODUCTION":
            return "https://api.phonepe.com/apis/pg"

        return "https://api-preprod.phonepe.com/apis/pg-sandbox"


settings = Settings()
