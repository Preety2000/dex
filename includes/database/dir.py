# ============================================================
# DATABASE CONFIGURATION
# ============================================================



from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# SQLite files will be created here:
# includes/core/sqlite/
DB_DIR = BASE_DIR / "sqlite"
DB_DIR.mkdir(parents=True, exist_ok=True)


MAIN_DB_URL = f"sqlite:///{DB_DIR / 'db_vidya.db'}"

EXAM_DB_URL = f"sqlite:///{DB_DIR / 'db_exam.db'}"

SECONDARY_DB_URLS: dict[str, str] = {"hindi": f"sqlite:///{DB_DIR / 'db_hindi.db'}"}


# MAIN_DB_URL = "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_vidya"

# EXAM_DB_URL = "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_exam"

# SECONDARY_DB_URLS: dict[str, str] = {
#     "hindi": "postgresql+psycopg://postgres:rajkamal@localhost:5432/db_hindi"
# }