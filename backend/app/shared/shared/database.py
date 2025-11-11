from typing import Any, Dict


class Database:
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or "sqlite:///:memory:"

    def status(self) -> Dict[str, Any]:
        return {"connected": True, "dsn": self.dsn}