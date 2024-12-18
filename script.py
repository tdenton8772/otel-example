import logging
import os
import time
import psutil
from threading import Thread
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
from opentelemetry.metrics import Observation, CallbackOptions

# 0. Setup for script
cpu_gauge = None
ram_gauge = None
disk_gauge = None
network_sent_gauge = None
network_recv_gauge = None

# Callback to gather CPU usage
def __get_cpu_usage_callback(_: CallbackOptions):
    for (number, percent) in enumerate(psutil.cpu_percent(percpu=True)):
        attributes = {"cpu_number": str(number)}
        yield Observation(percent, attributes)

# Callback to gather RAM memory usage
def __get_ram_usage_callback(_: CallbackOptions):
    ram_percent = psutil.virtual_memory().percent
    yield Observation(ram_percent)

# Callback to gather disk usage
def __get_disk_usage_callback(_: CallbackOptions):
    disk_percent = psutil.disk_usage('/').percent
    yield Observation(disk_percent)

# Callback to gather network sent bytes
def __get_network_sent_callback(_: CallbackOptions):
    net_sent = psutil.net_io_counters().bytes_sent
    yield Observation(net_sent)

# Callback to gather network received bytes
def __get_network_recv_callback(_: CallbackOptions):
    net_recv = psutil.net_io_counters().bytes_recv
    yield Observation(net_recv)

# Function to start a metric thread with its own reader
def start_metric_thread(callback, gauge_name, unit, description, resource):
    def metric_thread():
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
            export_interval_millis=1000
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        meter = meter_provider.get_meter(__name__)
        meter.create_observable_gauge(
            gauge_name, callbacks=[callback], unit=unit, description=description
        )
        while True:
            time.sleep(1)  # Keep the thread alive

    thread = Thread(target=metric_thread, daemon=True)
    thread.start()

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

# # Create example metrics
# cpu_usage = meter.create_observable_gauge(
#     "cpu_usage",
#     callbacks=[__get_cpu_usage_callback],
#     unit="%",
#     description="CPU usage"
# )
# memory_usage = meter.create_observable_gauge(
#     "memory_usage",
#     callbacks=[__get_ram_usage_callback],
#     unit="%",
#     description="Memory usage"
# )
# disk_usage = meter.create_observable_gauge(
#     "disk_usage",
#     callbacks=[__get_disk_usage_callback],
#     unit="%",
#     description="Disk usage"
# )
# network_sent = meter.create_observable_gauge(
#     "network_sent",
#     callbacks=[__get_network_sent_callback],
#     unit="bytes",
#     description="Network bytes sent"
# )
# network_recv = meter.create_observable_gauge(
#     "network_recv",
#     callbacks=[__get_network_recv_callback],
#     unit="bytes",
#     description="Network bytes received"
# )
# example_counter = meter.create_counter("example_counter", description="An example counter")
# example_counter.add(1, {"key": "value"})

# Start threads for each metric, each with its own MetricReader
start_metric_thread(__get_cpu_usage_callback, "cpu_usage", "%", "CPU usage", resource)
start_metric_thread(__get_ram_usage_callback, "memory_usage", "%", "Memory usage", resource)
start_metric_thread(__get_disk_usage_callback, "disk_usage", "%", "Disk usage", resource)
start_metric_thread(__get_network_sent_callback, "network_sent", "bytes", "Network bytes sent", resource)
start_metric_thread(__get_network_recv_callback, "network_recv", "bytes", "Network bytes received", resource)


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
logger.info("OpenTelemetry demo application starting...")

# Background function to generate spans and logs
def generate_spans_and_logs():
    while True:
        with tracer.start_as_current_span("periodic-span") as span:
            logger.info("This is a periodic log within a span context.")
            span.set_attribute("cpu.usage", psutil.cpu_percent())
            span.set_attribute("memory.usage", psutil.virtual_memory().percent)
            span.set_attribute("disk.usage", psutil.disk_usage('/').percent)
            span.set_attribute("network.sent", psutil.net_io_counters().bytes_sent)
            span.set_attribute("network.recv", psutil.net_io_counters().bytes_recv)
        time.sleep(10)

# Start a background thread for spans and logs
span_log_thread = Thread(target=generate_spans_and_logs, daemon=True)
span_log_thread.start()

# Keep the script running
try:
    while True:
        logger.info("Application is running and sending telemetry data...")
        time.sleep(30)
except KeyboardInterrupt:
    logger.info("Shutting down...")
    logger_provider.shutdown()