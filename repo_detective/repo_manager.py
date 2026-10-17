import os # Handles file paths and directories.
import re # Works with regular expressions to validate URLs.
import shutil # Deletes directories when needed.

from git import GitCommandError, Repo

WORKSPACE = "workspace" # It is a folder (directory), not a file.

# Only accepts https://github.com/owner/repo (optionally ending in .git or /)
GITHUB_URL = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)

# validates the URL
def parse_github_url(url):
    match = GITHUB_URL.match(url.strip())
    if not match:
        raise ValueError("Please enter a URL like https://github.com/owner/repo")
    return match.group(1), match.group(2)

# downloads the repository and returns its local path
def clone_repo(url):
    owner, name = parse_github_url(url)
    target = os.path.abspath(os.path.join(WORKSPACE, f"{owner}__{name}"))

    if os.path.isdir(target):
        return target  # already cloned earlier

    os.makedirs(WORKSPACE, exist_ok=True)
    try:
        # depth=50 downloads only the latest 50 commits (faster, smaller)
        # GIT_TERMINAL_PROMPT=0 stops git from asking for a password
        Repo.clone_from(
            f"https://github.com/{owner}/{name}.git",
            target,
            depth=50,
            env={"GIT_TERMINAL_PROMPT": "0"},
        )
    except GitCommandError:
        shutil.rmtree(target, ignore_errors=True)
        raise ValueError(
            "Could not clone. Is the repository public and the URL correct?"
        ) from None

    return target