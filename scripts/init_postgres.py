from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.db.postgres_adapter import PostgresAdapter

adapter = PostgresAdapter()
adapter.init_schema()
print("PostgreSQL schema initialized.")
