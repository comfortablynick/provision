"""Build argument parser for module."""
import argparse
import sys
from typing import NoReturn

from provision import apt, git, install


class ColoredArgParser(argparse.ArgumentParser):
    """Add color to ArgumentParser."""

    # RED : Error, GREEN : Okay, YELLOW : Warning, Blue: Help/Info
    color_dict = {"RED": "1;31", "GREEN": "1;32", "YELLOW": "1;33", "BLUE": "1;36"}

    def print_usage(self, file=None) -> None:
        """Add color to `Usage` messages."""
        if file is None:
            file = sys.stdout
        self._print_message(
            self.format_usage()[0].upper() + self.format_usage()[1:],
            file,
            self.color_dict["YELLOW"],
        )

    def print_help(self, file=None) -> None:
        """Colorize help message."""
        if file is None:
            file = sys.stdout
        self._print_message(
            self.format_help()[0].upper() + self.format_help()[1:],
            file,
            self.color_dict["BLUE"],
        )

    def _print_message(self, message, file=None, color=None) -> None:
        if message:
            if file is None:
                file = sys.stderr
            # Print messages in bold, colored text if color is given.
            if color is None:
                file.write(message)
            else:
                # \x1b[ is the ANSI Control Sequence Introducer (CSI)
                file.write("\x1b[" + color + "m" + message.strip() + "\x1b[0m\n")

    def exit(self, status=0, message=None) -> NoReturn:
        """Exit gracefully after printing message."""
        if message:
            self._print_message(message, sys.stderr, self.color_dict["RED"])
        sys.exit(status)

    def error(self, message) -> NoReturn:
        """Print argparse error."""
        self.print_usage(sys.stderr)
        args = {"prog": self.prog, "message": message}
        self.exit(2, "%(prog)s: Error: %(message)s\n" % args)


def build_parser() -> argparse.ArgumentParser:
    """Return an ArgumentParser object of all defined arguments/options."""
    parser = ColoredArgParser(
        prog="provision",
        description=__doc__,
        epilog="Use <command> -h/--help for command-specific options",
    )

    # Top-level options
    common_parser = argparse.ArgumentParser(add_help=False, parents=[parser])
    common_parser.add_argument(
        "-d",
        "--debug",
        action="count",
        default=0,
        help="More verbose log output; use one flag for INFO level and two for DEBUG",
    )
    common_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="force install/action to be completed",
    )
    subparsers = parser.add_subparsers(
        title="commands",
        description="(commands may take additional arguments)",
        metavar="<command>",
    )

    # All
    # parser_all = subparsers.add_parser("all", help="run all provisioning processes")
    # parser_all.set_defaults(func=run_all)

    # Apt
    parser_apt = subparsers.add_parser(
        "apt",
        help="use apt to manage system packages",
        description="",
        parents=[common_parser],
        add_help=False,
    )
    apt_subparsers = parser_apt.add_subparsers(
        title="subcommands",
        description="(subcommands may take additional arguments)",
        metavar="[COMMAND]",
    )

    # Apt install
    parser_apt_install = apt_subparsers.add_parser(
        "install",
        help="update apt cache and optionally install packages",
        description=apt.install.__doc__,
    )
    parser_apt_install.add_argument(
        "packages", nargs="*", help="optional apt packages to install"
    )
    parser_apt_install.set_defaults(func=apt.install)

    # Apt update
    parser_apt_update = apt_subparsers.add_parser(
        "update",
        aliases=["upgrade"],
        help="update all packages and clean old files",
        description=apt.update.__doc__,
    )
    parser_apt_update.add_argument(
        "packages", nargs="*", help="optional apt packages to install"
    )
    parser_apt_update.set_defaults(func=apt.update)

    # Install
    install_names = install.command_names()
    parser_install = subparsers.add_parser(
        "install",
        help="install software, building from source if needed",
        description="Download, (build), and install software:\n  {}".format(
            "\n  ".join(install_names)
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common_parser],
        add_help=False,
    )
    parser_install.add_argument(
        "install",
        help="app to build and install from source",
        choices=install_names,
        metavar="PROGRAM",
        nargs="+",
    )
    parser_install.set_defaults(func=install.main)

    # Github
    parser_github = subparsers.add_parser(
        "github",
        help="clone github repos",
        description=git.clone_git_repos.__doc__,
        parents=[common_parser],
        add_help=False,
    )
    parser_github.add_argument("dir", type=str, help="destination dir", default="~/git")
    parser_github.set_defaults(func=git.clone_git_repos)

    parser_github_release = subparsers.add_parser(
        "github-release",
        help="download and install release from github",
        description=git.github_latest_release.__doc__,
        parents=[common_parser],
        add_help=False,
    )
    parser_github_release.add_argument("repo", type=str, help="github repo name")
    parser_github_release.set_defaults(func=git.github_latest_release)

    return parser
