import argparse
import sys
from typing import NoReturn

"""Handle argument parsing for CLI."""


class ColoredArgParser(argparse.ArgumentParser):
    """Add color to ArgumentParser."""

    # RED : Error, GREEN : Okay, YELLOW : Warning, Blue: Help/Info
    colors = {
        "red": "1;31",
        "green": "1;32",
        "yellow": "1;33",
        "blue": "1;34",
        "cyan": "1;36",
        "magenta": "1;37",
        "reset": "1;00",
    }

    def print_usage(self, file=None) -> None:
        """Add color to `Usage` messages."""
        if file is None:
            file = sys.stdout
        self._print_message(
            self.format_usage()[0].upper() + self.format_usage()[1:],
            file,
            self.colors["yellow"],
        )

    def print_help(self, file=None) -> None:
        if file is None:
            file = sys.stdout
        self._print_message(
            self.format_help()[0].upper() + self.format_help()[1:],
            file,
            self.colors["cyan"],
        )

    def _print_message(self, message: str, file=None, color: str = None) -> None:
        if message:
            if file is None:
                file = sys.stderr
            if color is None:
                file.write(message)
            else:
                file.write("\x1b[" + color + "m" + message.strip() + "\x1b[0m\n")

    def exit(self, status=0, message=None) -> NoReturn:
        if message:
            self._print_message(message, sys.stderr, self.colors["red"])
        sys.exit(status)

    def error(self, message) -> NoReturn:
        self.print_usage(sys.stderr)
        args = {"prog": self.prog, "message": message}
        self.exit(2, "%(prog)s: Error: %(message)s\n" % args)


def process_args(argv: list):
    """Parse command line arguments and return namespace."""

    commands = "all", "apt", "install", "git"
    parser = ColoredArgParser(
        prog="provision",
        description="Helper module for setting up unix machines",
        epilog="use -h/--help for any command to see additional options",
    )

    parser.add_argument(
        "-d", "--debug", action="count", default=0, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "command", choices=commands, metavar="[COMMAND]", help=" | ".join(commands)
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="force install/action to be completed",
    )
    # subparsers = parser.add_subparsers(
    #     title="commands",
    #     description="(commands may take additional arguments)",
    #     metavar="[COMMAND]",
    # )
    #
    #     # All {{{2
    #     parser_all = subparsers.add_parser("all", help="run all provisioning processes")
    #     parser_all.set_defaults(func=run_all)
    #
    #     # Apt {{{2
    #     parser_apt = subparsers.add_parser(
    #         "apt",
    #         help="use apt to manage system packages",
    #         description="",
    #         parents=[common_parser],
    #         add_help=False,
    #     )
    #     apt_subparsers = parser_apt.add_subparsers(
    #         title="subcommands",
    #         description="(subcommands may take additional arguments)",
    #         metavar="[COMMAND]",
    #     )
    #
    #     # Apt install {{{3
    #     parser_apt_install = apt_subparsers.add_parser(
    #         "install",
    #         help="update apt cache and optionally install packages",
    #         description=Apt.install.__doc__,
    #     )
    #     parser_apt_install.add_argument(
    #         "packages", nargs="*", help="optional apt packages to install"
    #     )
    #     parser_apt_install.set_defaults(func=Apt.install)
    #
    #     # Apt update {{{3
    #     parser_apt_update = apt_subparsers.add_parser(
    #         "update",
    #         help="update all packages and clean old files",
    #         description=Apt.update.__doc__,
    #     )
    #     parser_apt_update.add_argument(
    #         "packages", nargs="*", help="optional apt packages to install"
    #     )
    #     parser_apt_update.set_defaults(func=Apt.update)
    #
    #     # Install {{{2
    # parser_install = subparsers.add_parser(
    #     "install",
    #     help="install software, building from source if needed",
    #     description="Download, (build), and install software",
    #     add_help=False,
    # )
    # parser_install.add_argument(
    #     "install",
    #     help="app to build and install from source",
    #     choices=["ctags", "fish", "mosh", "nnn", "tmux", "todo"],
    #     nargs="+",
    # )
    #     parser_install.set_defaults(func=install)
    #
    #     # Github {{{2
    #     parser_github = subparsers.add_parser(
    #         "github",
    #         help="clone github repos",
    #         description=clone_git_repos.__doc__,
    #         parents=[common_parser],
    #         add_help=False,
    #     )
    #     parser_github.add_argument("dir", type=str, help="destination dir", default="~/git")
    #     parser_github.set_defaults(func=clone_git_repos)
    #
    #     parser_github_release = subparsers.add_parser(
    #         "github-release",
    #         help="download and install release from github",
    #         description=github_latest_release.__doc__,
    #         parents=[common_parser],
    #         add_help=False,
    #     )
    #     parser_github_release.add_argument("repo", type=str, help="github repo name")
    #     parser_github_release.set_defaults(func=github_latest_release)
    # }}}
    # }}}
    return parser.parse_known_args(argv)
