import logging
from logging.handlers import TimedRotatingFileHandler

import streamlit as st

from osa_web.settings import ensure_runtime_paths, get_runtime_path


@st.cache_resource
def setup_logger(log_file_path):
    logger = logging.getLogger("Streamlit App")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_file_path = str(log_file_path)
    for handler in logger.handlers:
        if isinstance(handler, TimedRotatingFileHandler) and handler.baseFilename == log_file_path:
            return logger

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = TimedRotatingFileHandler(
        log_file_path,
        when="W6",
        interval=1,
        backupCount=4,
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


ensure_runtime_paths()
logger = setup_logger(get_runtime_path("log"))
