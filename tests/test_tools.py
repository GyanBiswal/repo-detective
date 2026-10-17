import pytest
from git import Repo

from repo_detective import tools
from repo_detective.repo_manager import parse_github_url


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "app.py").write_text("def hello():\n    return 'hi'\n\nclass Greeter:\n    pass\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "notes.txt").write_text("hello notes\n")
    git_repo = Repo.init(tmp_path)
    git_repo.index.add(["app.py", "docs/notes.txt"])
    git_repo.index.commit("first commit")
    return str(tmp_path)


def test_parse_valid_urls():
    assert parse_github_url("https://github.com/psf/requests") == ("psf", "requests")
    assert parse_github_url("https://github.com/psf/requests.git") == ("psf", "requests")
    assert parse_github_url("https://github.com/psf/requests/") == ("psf", "requests")


def test_parse_invalid_urls():
    bad_urls = [
        "https://evil.com/a/b",
        "not a url",
        "https://github.com/onlyowner",
        "http://github.com/a/b",
        "https://github.com/a/b; ls",
    ]
    for url in bad_urls:
        with pytest.raises(ValueError):
            parse_github_url(url)


def test_list_files(repo):
    result = tools.list_files(repo)
    assert "app.py" in result
    assert "docs/" in result
    assert ".git" not in result


def test_read_file_has_line_numbers(repo):
    result = tools.read_file(repo, "app.py")
    assert "1: def hello():" in result
    assert "4: class Greeter:" in result


def test_read_file_blocks_path_escape(repo):
    assert tools.read_file(repo, "../secret.txt").startswith("Error")


def test_read_missing_file(repo):
    assert tools.read_file(repo, "nope.py").startswith("Error")


def test_search_code(repo):
    result = tools.search_code(repo, "hello")
    assert "app.py:1" in result
    assert "docs/notes.txt:1" in result


def test_find_function(repo):
    assert "app.py:1" in tools.find_function(repo, "hello")
    assert "app.py:4" in tools.find_function(repo, "Greeter")


def test_git_history(repo):
    assert "first commit" in tools.git_history(repo)