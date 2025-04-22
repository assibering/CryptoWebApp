from logging.config import dictConfig

class CorrelationIdFilter:
    def __call__(self, record):
        from src.middleware.correlation_context import get_correlation_id
        record.correlation_id = get_correlation_id() or "-"
        return True

def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "correlation_id": "%(correlation_id)s", "logger": "%(name)s", "message": "%(message)s", "pathname": "%(pathname)s", "lineno": %(lineno)d}',
            },
        },
        "filters": {
            "correlation_id_filter": {
                "()": CorrelationIdFilter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["correlation_id_filter"],
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    })
