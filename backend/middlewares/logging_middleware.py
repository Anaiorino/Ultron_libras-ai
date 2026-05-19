import time
import uuid
import logging

from fastapi import Request
from backend.metrics import update_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("jarvis-api")


async def logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start_time = time.time()

    response = await call_next(request)

    process_time = round((time.time() - start_time) * 1000, 2)

    update_metrics(
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        response_time_ms=process_time,
        trace_id=trace_id
    )

    logger.info(
        f"trace_id={trace_id} | "
        f"method={request.method} | "
        f"path={request.url.path} | "
        f"status={response.status_code} | "
        f"time={process_time}ms"
    )

    response.headers["X-Trace-ID"] = trace_id

    return response