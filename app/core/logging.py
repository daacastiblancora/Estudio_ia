import logging
import sys
from app.core.config import settings

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("copiloto.log")
        ]
    )
    
    # Set third party log levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    
    return logging.getLogger("copiloto-core")

logger = setup_logging()
