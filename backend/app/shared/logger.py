import logging
import os


def setup_observability(service_name: str, app=None):
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4318")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    set_tracer_provider(provider)
    exporter = OTLPSpanExporter(endpoint=endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    RequestsInstrumentor().instrument()
    LoggingInstrumentor().instrument(set_logging_format=False)
    if app is not None:
        FastAPIInstrumentor().instrument_app(app)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        service = os.getenv("OTEL_SERVICE_NAME") or os.getenv("SERVICE_NAME") or name
        formatter = logging.Formatter(
            fmt='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"%(service)s","logger":"%(name)s","message":"%(message)s","trace_id":"%(otelTraceID)s","span_id":"%(otelSpanID)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logging.LoggerAdapter(logger, {"service": os.getenv("OTEL_SERVICE_NAME") or os.getenv("SERVICE_NAME") or name})
