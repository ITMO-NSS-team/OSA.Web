import logging
from logging.handlers import TimedRotatingFileHandler

import streamlit as st
import toml


@st.cache_resource
def setup_logger(log_file_path):
    logger = logging.getLogger("Streamlit App")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = TimedRotatingFileHandler(
        log_file_path,
        when="W6",
        interval=1,
        backupCount=4,
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = setup_logger(toml.load("config.toml")["paths"]["log"])
