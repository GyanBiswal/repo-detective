import os
import re

from git import GitCommandError, Repo

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
MAX_FILE_BYTES = 200_000  # skip huge files
MAX_LINES = 200           # max lines returned by read_file
MAX_RESULTS = 20          # max search results

# Make sure a file path stays inside the repository.
def safe_path(repo_path, relative_path):
    """Return the full path, but only if it stays inside the repo."""
    root = os.path.realpath(repo_path)
    full = os.path.realpath(os.path.join(root, relative_path))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("Path is outside the repository.")
    return full


# List files and folders.
def list_files(repo_path, directory="."):
    try:
        folder = safe_path(repo_path, directory)
    except ValueError as error:
        return f"Error: {error}"
    if not os.path.isdir(folder):
        return f"Error: '{directory}' is not a folder."

    names = []
    for name in sorted(os.listdir(folder)):
        if name in SKIP_DIRS:
            continue
        is_folder = os.path.isdir(os.path.join(folder, name))
        names.append(name + "/" if is_folder else name)
    return "\n".join(names[:200]) or "(empty folder)"


# Read the contents of a file.
def read_file(repo_path, path, start_line=1, end_line=200):
    try:
        full = safe_path(repo_path, path)
    except ValueError as error:
        return f"Error: {error}"
    if not os.path.isfile(full):
        return f"Error: file '{path}' not found."
    if os.path.getsize(full) > MAX_FILE_BYTES:
        return "Error: file is too large to read."

    try:
        with open(full, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except UnicodeDecodeError:
        return "Error: not a text file."

    start = max(start_line, 1)
    end = min(end_line, start + MAX_LINES - 1, len(lines))
    chunk = [f"{n}: {lines[n - 1]}" for n in range(start, end + 1)]
    if not chunk:
        return "(no lines in that range)"
    return "\n".join(chunk) + f"\n(lines {start}-{end} of {len(lines)})" # Returns the selected lines along with the total file length.


def _text_files(repo_path):
    """Yield (relative_path, full_path) for every readable file in the repo."""
    root = os.path.realpath(repo_path)
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            full = os.path.join(folder, name)
            if os.path.islink(full) or os.path.getsize(full) > MAX_FILE_BYTES:
                continue
            yield os.path.relpath(full, root), full

# Find where a function or class is defined.
def _search(repo_path, pattern):
    results = []
    for relative, full in _text_files(repo_path):
        try:
            with open(full, encoding="utf-8") as file:
                for number, line in enumerate(file, start=1):
                    if pattern.search(line):
                        results.append(f"{relative}:{number}: {line.strip()}")
                        if len(results) >= MAX_RESULTS:
                            return results
        except UnicodeDecodeError:
            continue  # skip binary files
    return results


# Search for specific text in the code.
def search_code(repo_path, query):
    if not query.strip():
        return "Error: query is empty."
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return "\n".join(_search(repo_path, pattern)) or "No matches found."


def find_function(repo_path, name):
    if not name.strip():
        return "Error: name is empty."
    # Matches: def name / class name / function name / func name / fn name
    pattern = re.compile(rf"\b(def|class|function|func|fn)\s+{re.escape(name)}\b")
    return "\n".join(_search(repo_path, pattern)) or "No definition found."

# View recent Git commits.
def git_history(repo_path, path="", max_count=5):
    max_count = min(max(max_count, 1), 20)
    if path:
        try:
            safe_path(repo_path, path)
        except ValueError as error:
            return f"Error: {error}"

    try:
        commits = list(Repo(repo_path).iter_commits(paths=path, max_count=max_count))
    except (GitCommandError, ValueError) as error:
        return f"Error: could not read git history ({error})"

    lines = []
    for commit in commits:
        date = commit.committed_datetime.strftime("%Y-%m-%d")
        title = commit.message.strip().split("\n")[0]
        lines.append(f"{commit.hexsha[:7]} {date} {commit.author.name}: {title}")
    return "\n".join(lines) or "No commits found."