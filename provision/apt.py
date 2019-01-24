"""Interact with apt-get on Debian distros."""
import argparse
import logging
import os
import shutil

from provision.arguments import ColoredArgParser
from provision.utils import run

LOG = logging.getLogger(__name__)


CACHE_UPDATED = False


def _update_cache() -> None:
    global CACHE_UPDATED
    if not CACHE_UPDATED:
        cmd = "sudo apt update -y"
        LOG.debug("Command: %s", cmd)
        run(cmd)
        CACHE_UPDATED = True


def _list_upgradable(args) -> int:
    LOG.debug("Apt cache updated: %s", CACHE_UPDATED)
    _update_cache()
    cmd = run("apt list --upgradable", capture_output=True)
    return cmd.returncode


def _upgrade(args=None) -> int:
    _update_cache()
    cmd = run("sudo apt full-upgrade -y", capture_output=True)
    return cmd.returncode


def install(args=None, pkgs: list = []) -> int:
    """Install apt packages, skipping if already installed."""
    _update_cache()
    # TODO: take cli args and add to pkg list if successful
    if not shutil.which("apt-get"):
        LOG.error("Apt not installed on this system")
        return 1
    packages = pkgs + args.packages
    if not len(packages):
        LOG.info("No pkgs supplied; getting apt pkgs from disk")
        pkg_file = "~/.config/shell/provision/apt_package"
        try:
            with open(os.path.expanduser(pkg_file), "r") as f:
                packages = f.read().splitlines()
        except FileNotFoundError:
            LOG.warning("apt pkg file not found at %s", pkg_file)
            return 1
    cmd = ["sudo", "apt", "install", "-y", *packages]
    LOG.debug("Command: %s", cmd)
    try:
        run(cmd)
    except FileNotFoundError:
        LOG.error("apt does not seem to be installed on this system.")
        return 1
    return 0


def update(args) -> int:
    """Install/update apt packages, and purge old cached files."""
    _update_cache()
    _upgrade(args)
    install(args)
    run("sudo apt autoremove", check=True)
    return run("sudo apt purge", capture_output=True).returncode


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
