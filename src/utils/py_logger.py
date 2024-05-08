import logging

log_format = (
    "%(asctime)s [%(levelname)s] - %(name)s - %(funcName)15s:%(lineno)d - %(message)s"
)

file_handler = logging.FileHandler("data/photo_share.log")
file_handler.setLevel(logging.INFO) 
file_handler.setFormatter(logging.Formatter(log_format))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG) 
stream_handler.setFormatter(logging.Formatter(log_format))


def get_logger(name):
    """
The get_logger function is a helper function that returns a logger object.
The logger object has two handlers: one for the console and one for the log file.
The logging level is set to DEBUG, which means that all messages will be logged.

:param name: Set the name of the logger
:return: A logger object
:doc-author: Trelent
"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger
