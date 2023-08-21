import logging

def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler()
    handler.setFormatter(
        fmt=logging.Formatter(fmt="%(levelname)s: %(asctime)s: %(name)s  %(message)s")
    )
    logger.addHandler(hdlr=handler)
    logger.setLevel(level=level)
    logger.propagate = False  # Prevent the modal client from double-logging.
    return logger
