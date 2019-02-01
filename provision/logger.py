"""Colored logger."""
import logging

import coloredlogs


def get_logger(log_name: str, log_level: int = logging.WARNING) -> logging.Logger:
    """Define defaults for color logger.

    Supported styles and colors can be found by running the
    ``humanfriendly --demo`` command.
    """
    log_fmt = "%(levelname)s:%(name)s:%(funcName)s: %(message)s"
    field_styles = dict(
        asctime=dict(color="green"),
        levelname=dict(color=245),
        programname=dict(color="cyan"),
        funcName=dict(color=172),
        name=dict(color="blue", bright=True),
    )
    level_styles = dict(
        debug=dict(color="green"),
        info=dict(color="yellow"),
        warning=dict(color="magenta"),
        error=dict(color="red"),
        critical=dict(color="red", bold=True),
    )
    log = logging.getLogger(log_name)
    coloredlogs.install(
        level=log_level,
        logger=log,
        fmt=log_fmt,
        level_styles=level_styles,
        field_styles=field_styles,
    )
    return log
