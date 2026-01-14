import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv("DB_NAME", "db_operations")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Construct the database URL
# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Add SSL mode if connecting to a remote server (e.g. Render)
if "localhost" not in DB_HOST and "127.0.0.1" not in DB_HOST:
    DATABASE_URL += "?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    """Returns a raw connection (for pandas read_sql)."""
    return engine.connect()

def get_db_session():
    """Returns a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
