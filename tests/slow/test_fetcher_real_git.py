# tests/slow/test_fetcher_real_git.py
"""
Tests that make real git calls. Run with: pytest -m slow
Requires git to be installed and on PATH.
"""
import subprocess
import yaml
import pytest
from pathlib import Path
from b1.core.fetcher import ModuleFetcher


@pytest.mark.slow
def test_fetcher_clones_git_repo(tmp_path):
    # Create a bare repo with a valid module structure
    bare_repo = tmp_path / "bare.git"
    work_tree = tmp_path / "work"
    work_tree.mkdir()

    subprocess.run(["git", "init", "--bare", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "init", str(work_tree)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.name", "Test"], check=True, capture_output=True)

    # Write a valid module into the work tree
    (work_tree / "b1-module.yaml").write_text(yaml.dump({
        "name": "real-module", "version": "1.0.0", "type": "development",
        "skills": [], "hooks": {},
    }), encoding="utf-8")
    subprocess.run(["git", "-C", str(work_tree), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "commit", "-m", "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "remote", "add", "origin", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "push", "-u", "origin", "HEAD"], check=True, capture_output=True)

    # Now test the fetcher against the bare repo using file:// URL
    # (The fetcher treats file:// as a git URL, deriving the cache dir name from the last path segment)
    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()

    result = fetcher.fetch(f"file://{bare_repo}")
    assert result.exists()
    assert (result / "b1-module.yaml").exists()


@pytest.mark.slow
def test_fetcher_pulls_on_second_fetch(tmp_path):
    bare_repo = tmp_path / "bare.git"
    work_tree = tmp_path / "work"
    work_tree.mkdir()

    subprocess.run(["git", "init", "--bare", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "init", str(work_tree)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.name", "Test"], check=True, capture_output=True)

    (work_tree / "b1-module.yaml").write_text(yaml.dump({
        "name": "bare", "version": "1.0.0", "type": "development",
        "skills": [], "hooks": {},
    }), encoding="utf-8")
    subprocess.run(["git", "-C", str(work_tree), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "commit", "-m", "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "remote", "add", "origin", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "push", "-u", "origin", "HEAD"], check=True, capture_output=True)

    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()

    url = f"file://{bare_repo}"
    fetcher.fetch(url)       # first: clone
    result = fetcher.fetch(url)  # second: pull (should not raise)
    assert result.exists()
