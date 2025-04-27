import contextvars

# Create a context var (thread-safe, async-safe)
_correlation_id_ctx_var = contextvars.ContextVar("correlation_id", default=None)

def set_correlation_id(correlation_id: str):
    _correlation_id_ctx_var.set(correlation_id)

def get_correlation_id() -> str:
    return _correlation_id_ctx_var.get()