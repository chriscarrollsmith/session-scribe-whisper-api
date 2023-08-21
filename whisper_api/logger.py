import logging
from logging import Logger

def get_logger(name, level=logging.INFO) -> Logger:
    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler()
    handler.setFormatter(
        fmt=logging.Formatter(fmt="%(levelname)s: %(asctime)s: %(name)s  %(message)s")
    )
    logger.addHandler(hdlr=handler)
    logger.setLevel(level=level)
    logger.propagate = False
    return logger
