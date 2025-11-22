import os


class _NoopTrace:
    def __init__(self, name: str):
        self.name = name
    def log(self, data):
        return None
    def end(self):
        return None


class Tracer:
    def __init__(self):
        self.host = os.getenv("LANGFUSE_HOST", "")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        self.client = None
        try:
            from langfuse import Langfuse
            if self.host and self.public_key and self.secret_key:
                self.client = Langfuse(host=self.host, public_key=self.public_key, secret_key=self.secret_key)
        except Exception:
            self.client = None

    def trace(self, name: str):
        if not self.client:
            return _NoopTrace(name)
        t = self.client.trace(name=name)
        return t


tracer = Tracer()
