import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging():
    """Configure logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Remove existing handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT.lower() == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create logger instance for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully", extra={
        "log_level": settings.LOG_LEVEL,
        "log_format": settings.LOG_FORMAT
    })

    return logger 