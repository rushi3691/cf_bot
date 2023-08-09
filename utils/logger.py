import logging
from logging import Handler, Logger

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

uvicorn_logger: Logger = logging.getLogger("uvicorn")
uvicorn_logger.propagate = False