"""Download, (build), and install programs."""
import logging
import shutil
from typing import List, NoReturn

from provision import apt, logger
from provision.git import git_latest_tag
from provision.utils import chdir, mkdir_p, rmtree, run

LOG = logger.get_logger(__name__, logging.DEBUG)


def install(args) -> int:
    """Install software, building from source if needed."""
    LOG.info("Install called for: %s", ", ".join(args.install))

    for item in args.install:
        func_name = f"install_{item}"
        try:
            LOG.debug("Calling '%s'", func_name)
            globals()[func_name](args)
        except KeyError:
            LOG.error("Function '%s' does not exist!", func_name)
            return 1
    return 0


def install_ctags(args) -> int:
    """Download, build, and install universal ctags."""
    if shutil.which("ctags") and not args.force:
        LOG.warning("ctags already exists. Skipping install!")
        return 1
    ctags_tmp = "/tmp/ctags"
    rmtree(ctags_tmp, ignore_errors=True)
    run(f"git clone https://github.com/universal-ctags/ctags.git {ctags_tmp}")

    with chdir(ctags_tmp):
        run("./autogen.sh")
        if run("./configure").returncode == 0:
            LOG.debug("ctags build configured. Running `make`")
            run("make")
        else:
            LOG.error("ctags build configure failed!")
            return 1
        LOG.debug("Installing ctags...")
        run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(ctags_tmp, ignore_errors=True)
    return 0


def install_lpass(args) -> int:
    """Download, build, and install lastpass CLI."""
    prog_name = "lpass"
    if shutil.which(prog_name) and not args.force:
        LOG.warning("%s already exists. Skipping install!", prog_name)
        return 1
    pkgs = [
        "bash-completion",
        "build-essential",
        "cmake",
        "libcurl4",
        "libcurl4-openssl-dev",
        "libssl-dev",
        "libxml2",
        "libxml2-dev",
        "libssl1.1",
        "pkg-config",
        "ca-certificates",
        "xclip",
    ]
    apt.install(args, pkgs=pkgs)
    tmp_dir = f"/tmp/{prog_name}"
    rmtree(tmp_dir, ignore_errors=True)
    run(f"git clone https://github.com/lastpass/lastpass-cli.git {tmp_dir}")

    with chdir(tmp_dir):
        run("make")
        LOG.debug("Installing %s...", prog_name)
        run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(tmp_dir, ignore_errors=True)
    return 0


def install_fish(args) -> int:
    """Download, build, and install the Friendly Interactive SHell."""
    if shutil.which("fish") and not args.force:
        LOG.warning("fish already exists. Skipping install!")
        return 1
    pkgs = [
        "build-essential",
        "ncurses-dev",
        "libncurses5-dev",
        "gettext",
        "autoconf",
        "doxygen",
    ]
    apt.install(args, pkgs=pkgs)
    fish_tmp = "/tmp/fish"
    rmtree(fish_tmp, ignore_errors=True)
    run(f"git clone https://github.com/fish-shell/fish-shell.git {fish_tmp}")

    with chdir(fish_tmp):
        run("mkdir build")

        with chdir("./build"):
            run("cmake ..")
            run("make")
            LOG.debug("Installing fish...")
            run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(fish_tmp, ignore_errors=True)
    return 0


def install_tmux(args) -> int:
    """Download, build, and install tmux terminal multiplexer."""
    if shutil.which("tmux") and not args.force:
        LOG.warning("tmux already exists. Skipping install!")
        return 1
    pkgs = [
        "git",
        "automake",
        "build-essential",
        "pkg-config",
        "libevent-dev",
        "libncurses5-dev",
    ]
    apt.install(args, pkgs)
    tmux_tmp = "/tmp/tmux"
    rmtree(tmux_tmp, ignore_errors=True)
    run(f"git clone https://github.com/tmux/tmux.git {tmux_tmp}")

    with chdir(tmux_tmp):
        tag = run("git describe --tags --abbrev=0", capture_output=True).stdout.strip(
            "\n"
        )
        LOG.info("Checking out most recent tmux release: %s", tag)
        run(f"git checkout {tag}")
        run("sh autogen.sh")
        if run("./configure").returncode == 0:
            LOG.debug("tmux build configured. Running `make`")
            run("make")
        else:
            LOG.error("tmux build configure failed!")
            return 1
        LOG.debug("Installing tmux...")
        run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(tmux_tmp, ignore_errors=True)
    return 0


def install_mosh(args) -> int:
    """Download, build, and install mobile shell."""
    if shutil.which("mosh") and not args.force:
        LOG.warning("mosh already exists. Skipping install!")
        return 1
    pkgs = [
        "protobuf-compiler",
        "libprotobuf-dev",
        "libutempter-dev",
        "libboost-dev",
        "libio-pty-perl",
        "libssl-dev",
        "pkg-config",
        "autoconf",
    ]
    apt.install(args, pkgs)
    mosh_tmp = "/tmp/mosh"
    rmtree(mosh_tmp, ignore_errors=True)
    run(f"git clone https://github.com/keithw/mosh.git {mosh_tmp}")

    with chdir(mosh_tmp):
        run("sh autogen.sh")
        if run("./configure").returncode == 0:
            LOG.debug("mosh build configured. Running `make`")
            run("make")
        else:
            LOG.error("mosh build configure failed!")
        LOG.debug("Installing mosh...")
        run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(mosh_tmp, ignore_errors=True)
    return 0


def install_neovim(args) -> int:
    """Download, build, and install Neovim."""
    prog_name = "nvim"
    if shutil.which(prog_name) and not args.force:
        LOG.warning("%s already exists. Skipping install!", prog_name)
        return 1
    pkgs = [
        "gperf",
        "libluajit-5.1-dev",
        "libunibilium-dev",
        "libmsgpack-dev",
        "libtermkey-dev",
        "libvterm-dev",
        "libjemalloc-dev",
    ]
    apt.install(args, pkgs=pkgs)
    tmp_dir = f"/tmp/{prog_name}"
    rmtree(tmp_dir, ignore_errors=True)
    run(f"git clone https://github.com/neovim/neovim.git {tmp_dir}")

    LOG.info("Building dependencies...")
    deps_dir = f"{tmp_dir}/.deps"
    mkdir_p(deps_dir)
    with chdir(deps_dir):
        cmake = run("cmake ../third-party", capture_output=True)
        if cmake.returncode == 0:
            run("make")
    LOG.info("Building %s...", prog_name)
    with chdir(tmp_dir):
        run("make distclean")
        run("make CMAKE_BUILD_TYPE=RelWithDebInfo")
        LOG.info("Installing %s...", prog_name)
        run("sudo make install")
    LOG.debug("Cleaning up temp directories...")
    rmtree(tmp_dir, ignore_errors=True)
    return 0


def install_nnn(args) -> int:
    """Download, install and build nnn file manager."""
    if shutil.which("nnn") and not args.force:
        LOG.warning("nnn already exists. Skipping install!")
        return 1
    pkgs = ["pkg-config", "libncursesw5-dev"]
    apt.install(args, pkgs)
    nnn_tmp = "/tmp/nnn"
    rmtree(nnn_tmp, ignore_errors=True)
    run(f"git clone https://github.com/jarun/nnn.git {nnn_tmp}")

    with chdir(nnn_tmp):
        tag = git_latest_tag()
        LOG.info("Checking out most recent nnn release: %s", tag)
        if run(f"git checkout {tag}").returncode == 0:
            run("make")
            LOG.debug("Installing nnn...")
            run("sudo make install")
        else:
            LOG.error("Checkout for latest version of `nnn` failed. Aborting install!")
            LOG.debug("Cleaning up temp directories...")
    rmtree(nnn_tmp, ignore_errors=True)
    return 0


def install_todo(args) -> int:
    """Download and install todo.txt cli."""
    if shutil.which("todo.sh") and not args.force:
        LOG.warning("todo.sh already exists. Skipping install!")
        return 1

    todo_tmp = "/tmp/todo"
    rmtree(todo_tmp, ignore_errors=True)
    run(f"git clone https://github.com/todotxt/todo.txt-cli.git {todo_tmp}")

    with chdir(todo_tmp):
        run("make")
        install = run("sudo make install", capture_output=True)
    rmtree(todo_tmp)
    return install.returncode


def install_vcprompt(args) -> int:
    """Download and install vcprompt C utility for git status."""
    if shutil.which("vcprompt") and not args.force:
        LOG.warning("vcprompt already exists. Skipping install!")
        return 1

    vcp_tmp = "/tmp/vcprompt"
    rmtree(vcp_tmp, ignore_errors=True)
    run(f"hg clone https://bitbucket.org/gward/vcprompt {vcp_tmp}")

    with chdir(vcp_tmp):
        run("autoconf")
        run("./configure")
        run("make")
        install = run("sudo make install")
    rmtree(vcp_tmp)
    return install.returncode


def command_names() -> List[str]:
    """Return globals of this script."""
    return [d.split("_")[1] for d in globals().keys() if d.startswith("install_")]


def main(args) -> NoReturn:
    """Direct `args` to correct function."""
    for prog in args.install:
        prog_name = f"install_{prog}"
        globals()[prog_name](args)
