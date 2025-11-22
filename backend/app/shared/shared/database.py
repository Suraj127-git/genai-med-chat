from typing import Any, Dict, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from shared.config import settings

Base = declarative_base()


class Database:
    def __init__(self) -> None:
        self.dsn = settings.MYSQL_DSN
        self.engine = create_engine(self.dsn, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def status(self) -> Dict[str, Any]:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                return {"connected": True, "dsn": self.dsn}
        except Exception as e:
            return {"connected": False, "error": str(e)}