"""
OpenTelemetry Configuration for SmartGriev
Distributed tracing with OTLP export
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def configure_opentelemetry():
    """
    Configure OpenTelemetry for distributed tracing
    
    Call this function during Django app initialization
    """
    if not getattr(settings, 'ENABLE_OPENTELEMETRY', False):
        logger.info("OpenTelemetry disabled via settings")
        return
    
    try:
        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: "smartgriev",
            SERVICE_VERSION: getattr(settings, 'APP_VERSION', '1.0.0'),
            "deployment.environment": getattr(settings, 'ENVIRONMENT', 'development'),
        })
        
        # Configure tracer provider
        tracer_provider = TracerProvider(resource=resource)
        
        # Add OTLP exporter (sends to Jaeger, Zipkin, or any OTLP-compatible backend)
        otlp_endpoint = getattr(settings, 'OTLP_ENDPOINT', 'http://localhost:4317')
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True  # Use True for local dev, False for production with TLS
        )
        
        tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        
        # Set the global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        # Auto-instrument Django
        DjangoInstrumentor().instrument()
        
        # Auto-instrument database
        Psycopg2Instrumentor().instrument()
        
        # Auto-instrument Redis
        RedisInstrumentor().instrument()
        
        # Auto-instrument outgoing HTTP requests
        RequestsInstrumentor().instrument()
        
        logger.info(
            f"OpenTelemetry configured successfully. "
            f"Exporting traces to {otlp_endpoint}"
        )
        
    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry: {e}")


def get_tracer(name: str = __name__):
    """
    Get a tracer instance for custom spans
    
    Usage:
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("my_operation"):
            # Your code here
            pass
    """
    return trace.get_tracer(name)
