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
        self.endpoint = os.getenv("LANGSMITH_ENDPOINT", "")
        self.api_key = os.getenv("LANGSMITH_API_KEY", "")
        self.project = os.getenv("LANGSMITH_PROJECT", "")
        self.enabled = os.getenv("LANGSMITH_TRACING", "").lower() in ("1", "true", "yes")
        self.client = None
        try:
            from langsmith import Client
            if self.enabled and self.api_key and self.endpoint:
                self.client = Client(api_url=self.endpoint, api_key=self.api_key, project_name=self.project or None)
        except Exception:
            self.client = None

    def trace(self, name: str):
        if not self.client:
            return _NoopTrace(name)
        try:
            run = self.client.create_run(run_type="chain", name=name)
            class _RunWrapper:
                def __init__(self, client, run_id):
                    self.client = client
                    self.run_id = run_id
                def log(self, data):
                    try:
                        self.client.update_run(self.run_id, inputs=data if isinstance(data, dict) else {"data": data})
                    except Exception:
                        pass
                def end(self):
                    try:
                        self.client.end_run(self.run_id)
                    except Exception:
                        pass
            return _RunWrapper(self.client, run["id"]) if isinstance(run, dict) and run.get("id") else _NoopTrace(name)
        except Exception:
            return _NoopTrace(name)


tracer = Tracer()
