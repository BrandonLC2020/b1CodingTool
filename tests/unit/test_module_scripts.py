"""Cross-module invariants for scripts shipped inside modules/.

These tests catch silent-failure regressions like a module's `post-install.sh`
losing its executable bit — the hook engine would fail to invoke it at install
time and the user would see no obvious error.
"""
import os
from pathlib import Path

import pytest

MODULES_ROOT = Path(__file__).resolve().parents[2] / "modules"

POST_INSTALL_SCRIPTS = sorted(MODULES_ROOT.glob("**/scripts/post-install.sh"))


@pytest.mark.parametrize(
    "script_path",
    POST_INSTALL_SCRIPTS,
    ids=[str(p.relative_to(MODULES_ROOT)) for p in POST_INSTALL_SCRIPTS],
)
def test_post_install_script_is_executable(script_path: Path):
    """Every modules/<...>/scripts/post-install.sh must have its executable bit set.

    The hook engine (`src/b1/core/hook_engine.py`) invokes these scripts directly
    at `b1 install` time. A missing executable bit results in a silent failure
    that the rest of the test suite would not catch.
    """
    assert os.access(script_path, os.X_OK), f"{script_path} is not executable"


def test_post_install_scripts_were_discovered():
    """Guard against the glob returning nothing — would silently skip all parametrized cases."""
    assert POST_INSTALL_SCRIPTS, "expected to find at least one post-install.sh under modules/"
