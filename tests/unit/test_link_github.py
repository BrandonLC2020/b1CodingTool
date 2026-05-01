import pytest
from b1.commands.link_github import extract_github_slug

@pytest.mark.parametrize("input_str,expected", [
    ("https://github.com/owner/repo", ("owner", "repo")),
    ("git@github.com:owner/repo.git", ("owner", "repo")),
    ("owner/repo", ("owner", "repo")),
    ("https://github.com/owner/repo.git", ("owner", "repo")),
    ("invalid", None),
])
def test_extract_github_slug(input_str, expected):
    assert extract_github_slug(input_str) == expected
