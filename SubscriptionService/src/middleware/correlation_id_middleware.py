import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.middleware.correlation_context import set_correlation_id

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Save in context var
        set_correlation_id(correlation_id)
        
        # Make it available to response too
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
