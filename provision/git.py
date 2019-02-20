"""Handle interactions with github."""
import logging
import os
import shutil

import requests
from github import Github
from provision.utils import chdir, run

LOG = logging.getLogger(__name__)


def git_clone(repo: str, dest_path: str = "", args: list = ["--recursive"]) -> None:
    """Clone git repo to dest path."""
    if not shutil.which("git"):
        LOG.error("Git not installed!")
        return
    if not repo[0:4] in ("git@", "http"):
        # Assume it's my repo
        repo = f"git@github.com:comfortablynick/{repo}.git"
    if dest_path is not None:
        args.append(os.path.expanduser(dest_path))
    cmd = ["git", "clone", repo, *args]
    LOG.debug("Cmd: %s", " ".join(cmd))
    with chdir(os.path.expanduser("~/git")):
        run(cmd)
    return


def github_token() -> str:
    """Retrieve secret access token from disk."""
    file = os.path.expanduser("~/.github_token")
    token = ""
    try:
        with open(file, "r") as f:
            token = f.read()
    except FileNotFoundError:
        LOG.error("GitHub token file not found: %s. Aborting!", file)
        return ""
    else:
        return token.strip("\n")


def clone_git_repos(args) -> None:
    """Clone repos from GitHub."""
    token = github_token()
    LOG.info("GitHub token found: %s", token)
    if token == "":
        return
    g = Github(token)
    for repo in g.get_user().get_repos():
        root_files = [content.name for content in repo.get_contents(".")]
        if ".provision_ignore" not in root_files:
            git_clone(repo.ssh_url)


def git_latest_tag() -> str:
    """Return first tag after reverse sort of available tags."""
    return run("git describe --tags --abbrev=0", capture_output=True).stdout.strip("\n")


def github_latest_release(args) -> int:
    """Get latest release binary."""
    token = github_token()
    if token == "":
        LOG.error("No GitHub token found!")
        return 1
    LOG.info("GitHub token found: %s", token)
    g = Github(token)
    r = g.get_repo(args.repo)
    name = r.name

    if shutil.which(name) and not args.force:
        LOG.warning("%s already exists. Skipping install!", name)
        return 1
    rel = r.get_releases()[0]  # latest
    assets = rel.get_assets()
    if assets.totalCount is None:
        LOG.error("Repo '%s' has no assets", args.repo)
        return 1
    print("Choose from the following packages:")
    for ctr, asset in enumerate(assets, 1):
        print(f"{str(ctr)}: {asset.name}")
    while True:
        choice = input("Enter number of choice: ")
        if choice == "":
            LOG.error("User input canceled!")
            return 1
        try:
            file = assets[int(choice) - 1]
        except IndexError:
            LOG.error("Choice '%s' out of range!", str(choice))
            continue
        except ValueError:
            LOG.error("Incorrect value: '%s'. Enter a number in range.", str(choice))
            continue
        else:
            break
    print(f"You chose to download {file.name}")
    r = requests.get(file.browser_download_url, stream=True)
    LOG.debug("Request response: %s", r.status_code)
    dest_path = os.path.join(os.path.expanduser(args.dest), file.name)
    print(f"Downloading to {dest_path}...")
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
    return 0
