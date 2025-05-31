from loguru import logger
import sys
from app.config import settings

logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL, format="[{time}] {level} - {message}")
