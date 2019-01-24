import logging
import sys

from provision import apt, arguments

log_fmt = "%(levelname)s:%(funcName)s: %(message)s"
logging.basicConfig(format=log_fmt)
LOG = logging.getLogger(__name__)


def main():
    """Command-line entry point."""
    # Get arguments
    try:
        sys.argv[1]
        cli_args = sys.argv[1:]
    except IndexError:
        cli_args = ["-dd", "--help"]
    finally:
        args, extra = arguments.process_args(cli_args)

    if args.debug == 1:
        log_level = logging.INFO
    elif args.debug >= 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    try:
        import coloredlogs
    except ModuleNotFoundError:
        pass
    else:
        coloredlogs.install(logger=LOG, fmt=log_fmt, level=log_level)

    LOG.info("Logging level: %s", LOG.getEffectiveLevel())
    LOG.info("Argument input: %s", repr(cli_args))
    LOG.info("Argparse output: %s", repr(args))

    if len(extra):
        LOG.info("Argparse extra args: %s", repr(extra))

    if args.command == "apt":
        apt.main(cli_args)
