"""Utility functions"""
import errno
import logging
import os
import shutil
import stat
import subprocess
import warnings
from contextlib import contextmanager
from pathlib import Path
from shlex import split
from typing import Generator

LOG = logging.getLogger(__name__)


def run(cmd, encoding="utf-8", *args, **kwargs):
    """Run subprocess command

    A string command will be split into a list for subprocess.run()."""
    if not isinstance(cmd, list):
        cmd = split(cmd)
    return subprocess.run(cmd, *args, **kwargs, encoding=encoding)


def mkdir_p(newdir: str) -> None:
    """Make new directory if it doesn't exist.

    Emulates `mkdir -p`
        - if it already exists, silently complete
        - if regular file in the way, raise an exception
        - if parent directories do not exist, make them as well
        From: Pipenv (http://bit.ly/2SLxRwL)
    """
    if os.path.isdir(newdir):
        LOG.debug("%s already exists", newdir)
        pass
    elif os.path.isfile(newdir):
        raise OSError(
            f"a file with the same name as the desired dir, '{newdir}', already exists."
        )

    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir_p(head)
        if tail:
            # Even though we've checked that the directory doesn't exist above, it might exist
            # now if some other process has created it between now and the time we checked it.
            try:
                os.mkdir(newdir)
            except OSError as exn:
                # If we failed because the directory does exist, that's not a problem -
                # that's what we were trying to do anyway. Only re-raise the exception
                # if we failed for some other reason.
                if exn.errno != errno.EEXIST:
                    raise


def set_write_bit(file_name: str) -> None:
    """Make file writable."""
    if isinstance(file_name, str) and not os.path.exists(file_name):
        return
    os.chmod(file_name, stat.S_IWRITE | stat.S_IWUSR | stat.S_IRUSR)
    return


def rmtree(directory: str, ignore_errors=False):
    """Remove directory and contents."""
    LOG.debug("Removing directory tree %s", directory)
    shutil.rmtree(
        directory, ignore_errors=ignore_errors, onerror=handle_remove_readonly
    )


def handle_remove_readonly(func, path: str, exc) -> None:
    """Error handler for shutil.rmtree.

    Windows source repo folders are read-only by default, so this error handler
    attempts to set them as writeable and then proceed with deletion.
    """
    # Check for read-only attribute
    default_warning_message = (
        "Unable to remove file due to permissions restriction: {!r}"
    )
    # split the initial exception out into its type, exception, and traceback
    exc_type, exc_exception, exc_tb = exc
    if is_readonly_path(path):
        # Apply write permission and call original function
        set_write_bit(path)
        try:
            func(path)
        except (OSError, IOError) as e:
            if e.errno in [errno.EACCES, errno.EPERM]:
                warnings.warn(default_warning_message.format(path), ResourceWarning)
                return

    if exc_exception.errno in [errno.EACCES, errno.EPERM]:
        warnings.warn(default_warning_message.format(path), ResourceWarning)
        return

    raise


def is_readonly_path(file_name: str) -> bool:
    """Check if a provided path exists and is readonly.

    Permissions check is `bool(path.stat & stat.S_IREAD)`
    or `not os.access(path, os.W_OK)`
    """
    if os.path.exists(file_name):
        return bool(os.stat(file_name).st_mode & stat.S_IREAD) or not os.access(
            file_name, os.W_OK
        )

    return False


@contextmanager
def chdir(path: str) -> Generator:
    """Context manager to change working directories.

    Usage:
        `with chdir(/path/to/execute/cmd/in):`
    """
    if not path:
        return
    prev_cwd = Path.cwd().as_posix()
    if isinstance(path, Path):
        path = path.as_posix()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)
