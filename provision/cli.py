"""Command-line interface for provision."""
import logging
import sys

import coloredlogs
from provision.args import build_parser


def get_logger(log_name: str, log_level: int) -> logging.Logger:  # {{{1
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


# Entry point
def cli() -> int:
    """Admin script for provisioning software/settings on unix machines."""
    try:
        sys.argv[1]
        cli_args = sys.argv[1:]
    except IndexError:
        cli_args = ["--help"]
    finally:
        args, extra = build_parser().parse_known_args(cli_args)

    if args.debug == 1:
        log_level = logging.INFO
    elif args.debug >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    LOG = get_logger(log_name=__name__, log_level=log_level)
    LOG.info("Logging level: %s", LOG.getEffectiveLevel())
    LOG.info("Argument input: %s", repr(cli_args))
    LOG.info("Argparse output: %s", repr(args))

    try:
        args.func(args)
    except AttributeError as e:
        LOG.error(
            "No function is associated with command input: %r\nError text:%s", args, e
        )
    return 0
