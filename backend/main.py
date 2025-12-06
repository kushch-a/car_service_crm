import time
import uuid
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. ДОДАНО ІМПОРТ
from passlib.context import CryptContext
import logging
from opentelemetry import trace

# ... (Ваші OpenTelemetry імпорти залишаються без змін) ...
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Local Imports
from db import connect_to_db, disconnect_from_db, database
from routers import customers, cars, services, auth, invoices, invoice_items, users
from shared_state import rate_limit_store

# --- Constants ---
WINDOW_MS = 2000
MAX_REQUESTS = 30

# ... (OpenTelemetry Setup залишається без змін) ...
resource = Resource(attributes={
    "service.name": os.getenv("OTEL_SERVICE_NAME", "sto-crm-backend"),
    "deployment.environment": os.getenv("APP_ENV", "development")
})
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")

# Traces, Metrics, Logs setup... (без змін)
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")))
trace.set_tracer_provider(trace_provider)

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{otlp_endpoint}/v1/metrics"),
    export_interval_millis=2000
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
set_meter_provider(meter_provider)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{otlp_endpoint}/v1/logs")))
set_logger_provider(logger_provider)

handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)


# --- FastAPI App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    yield
    await disconnect_from_db()


app = FastAPI(
    title="CRM для СТО",
    description="System for Car Service",
    version="1.0.0",
    lifespan=lifespan
)

# --- 2. CORS CONFIGURATION (НОВИЙ БЛОК) ---
# Це виправить помилку 405 для OPTIONS запитів
origins = [
    "http://localhost:3000",  # React / Next.js за замовчуванням
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite за замовчуванням
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Дозволені джерела
    allow_credentials=True,  # Дозволяє cookies/authorization headers
    allow_methods=["*"],  # Дозволяє всі методи (GET, POST, OPTIONS, PUT, DELETE)
    allow_headers=["*"],  # Дозволяє всі заголовки
)
# ------------------------------------------

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app, meter_provider=meter_provider)


# --- Middlewares ---
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    # ... (Ваш код логування без змін) ...
    start_time = time.time()
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id
    span_id = span.get_span_context().span_id

    response = await call_next(request)

    duration = time.time() - start_time

    log_details = {
        "http.method": request.method,
        "http.url": str(request.url),
        "http.status_code": response.status_code,
        "http.duration_ms": round(duration * 1000, 2),
        "http.client_ip": request.client.host,
        "trace_id": format(trace_id, 'x'),
        "span_id": format(span_id, 'x'),
    }

    message = f'{request.client.host} - "{request.method} {request.url.path} HTTP/1.1" {response.status_code}'

    if 400 <= response.status_code < 500:
        logging.warning(message, extra=log_details)
    elif response.status_code >= 500:
        logging.error(message, extra=log_details)
    else:
        logging.info(message, extra=log_details)

    return response


# ... (other middlewares & handlers) ...

@app.exception_handler(Exception)
async def unified_error_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception for {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "internal_error"})


# --- Routers ---
app.include_router(customers.router)
app.include_router(cars.router)
app.include_router(services.router)
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(invoice_items.router)
app.include_router(users.router)


# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "CRM API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/error")
async def trigger_error():
    logging.error("This is a simulated error endpoint.")
    return JSONResponse(status_code=500, content={"error": "simulated_error"})


logging.info("Backend service started and configured for OTLP logging.")