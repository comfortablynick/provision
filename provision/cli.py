"""Command-line interface for provision."""
import logging
import sys

from provision.args import build_parser
from provision.logger import get_logger


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
