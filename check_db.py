import sys
import os
import sqlalchemy
from sqlalchemy import text

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from db.database import engine
    print("Checking connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(f"Connected successfully! Server version: {result.fetchone()[0]}")
except Exception as e:
    print(f"Connection failed: {e}")
