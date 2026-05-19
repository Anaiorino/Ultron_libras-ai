metrics_data = {
    "total_requests": 0,
    "total_response_time_ms": 0,
    "average_response_time_ms": 0,
    "last_path": None,
    "last_method": None,
    "last_status_code": None,
    "last_trace_id": None
}


def update_metrics(
    path: str,
    method: str,
    status_code: int,
    response_time_ms: float,
    trace_id: str
):
    metrics_data["total_requests"] += 1
    metrics_data["total_response_time_ms"] += response_time_ms

    metrics_data["average_response_time_ms"] = round(
        metrics_data["total_response_time_ms"] / metrics_data["total_requests"],
        2
    )

    metrics_data["last_path"] = path
    metrics_data["last_method"] = method
    metrics_data["last_status_code"] = status_code
    metrics_data["last_trace_id"] = trace_id


def get_metrics():
    return metrics_data