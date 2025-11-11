"""
Initialize MySQL tables using shared SQLAlchemy metadata/engine.
Run after MySQL is available.
"""
import os
import sys

# Add shared package path dynamically for imports
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend
SHARED_DIR = os.path.join(BASE_DIR, "microservices-python", "shared")
sys.path.append(SHARED_DIR)

from shared.mysql_repo import metadata, engine  # type: ignore


def main():
    print("Creating tables (if not exist)...")
    metadata.create_all(engine)
    print("Done.")


if __name__ == "__main__":
    main()
