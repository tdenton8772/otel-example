import logging
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

# Retrieve OTLP endpoint from environment variable or default to localhost
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

# Set up resource attributes for better traceability
resource = Resource.create(
    {
        "service.name": "example-service",
        "service.instance.id": "instance-1",
    }
)

# 1. Set up the Tracer Provider for spans
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure the OTLP exporter for spans
otlp_span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 2. Set up the Meter Provider for metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Create an example counter metric
counter = meter.create_counter("example_counter", description="An example counter")

# Record a metric
counter.add(1, {"key": "value"})

# 3. Set up Logger Provider for logs
logger_provider = LoggerProvider(resource=resource)
otlp_log_exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
log_processor = BatchLogRecordProcessor(otlp_log_exporter)
logger_provider.add_log_record_processor(log_processor)

# Configure Python logging to use OpenTelemetry
logging_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.basicConfig(level=logging.INFO)
logging.getLogger().addHandler(logging_handler)

# Log messages
logger = logging.getLogger(__name__)
logger.info("This is an example log message!")

# 4. Example usage of spans
with tracer.start_as_current_span("example-span"):
    logger.info("Logging within a span context!")
    print("Hello, OpenTelemetry!")

    # Record another metric inside the span
    counter.add(2, {"key": "span_metric"})

# Shut down the LoggerProvider to flush logs before exiting
logger_provider.shutdown()
