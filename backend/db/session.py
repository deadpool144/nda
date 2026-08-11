import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_db_path = os.path.join(BASE_DIR, "contracts_v2.db")

# Allow database URL override via environment variables (useful for cloud deployments like Render)
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{default_db_path}")

# If SQLite is used, ensure we handle the relative path or direct path correctly
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # If the user passed a file path, format it as a sqlite connection string
    if not SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        # e.g., if DATABASE_URL is just /data/contracts_v2.db
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLALCHEMY_DATABASE_URL.replace('sqlite://', '')}"

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
