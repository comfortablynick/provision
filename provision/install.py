import logging

from provision.arguments import ColoredArgParser

LOG = logging.getLogger(__name__)


def main(cli_args):
    LOG.debug(cli_args)
    parser = ColoredArgParser(
        prog="provision install",
        description="Install software",
        epilog="use -h/--help for any command to see additional options",
    )
    parser.add_argument(
        "command",
        help="app to build and install from source",
        choices=["ctags", "fish", "mosh", "nnn", "tmux", "todo"],
        nargs="+",
    )
    args = parser.parse_known_args(cli_args)
    LOG.debug(args)
