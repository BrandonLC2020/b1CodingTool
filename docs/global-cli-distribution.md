# Plan: Make `b1` Available as a Global CLI Command

## Goal

Open a terminal, navigate to any directory, and type `b1 init` — no `uv run` prefix, no virtual environment activation, no path tricks.

## Why `uv run b1` Is Required Today

The `[project.scripts]` entry point is already correctly defined in `pyproject.toml`:

```toml
[project.scripts]
b1 = "b1.cli:main"
```

When a Python package with this declaration is **installed** by pip, uv, or any installer, the installer writes a small wrapper script (e.g., `~/.local/bin/b1`) that activates the right environment and calls `b1.cli:main`. That script is on `PATH`, so `b1` just works.

`uv run b1` bypasses installation entirely — it finds the local project, spins up a temporary env, and runs the script. This works for development but produces nothing on `PATH`.

The fix is distribution: install the package globally in a way that puts the `b1` script on `PATH`.

---

## Blocker: Fix `requires-python` First

`pyproject.toml` currently declares:

```toml
requires-python = ">=3.14"
```

Python 3.14 is in beta as of April 2026. This constraint blocks installation on virtually every machine.

A codebase audit confirms the code uses only Python 3.9+ features (`list[str]` generics via PEP 585). No 3.10, 3.12, 3.13, or 3.14-specific syntax is present.

**Recommended fix before any distribution work:**

```toml
requires-python = ">=3.12"
```

Python 3.12 (released Oct 2023, supported through Oct 2028) is the right floor:
- It is the current de-facto LTS for new Python projects
- All major tools (uv, Ruff, mypy) optimize for it
- Sets a reasonable baseline without restricting future use of 3.12 features (`type` statement, improved error messages, f-string expressions)

---

## Distribution Options

### Option A — `uv tool install` (Immediate, No Publishing Required)

`uv tool` is uv's equivalent of `pipx`: it installs a Python CLI into an isolated environment and puts the script on `PATH`. No PyPI account, no publishing, works today.

**Install from the local repo:**
```bash
cd /path/to/b1CodingTool
uv tool install .
b1 --help   # works immediately
```

**Install from a git URL (shareable with others who have access):**
```bash
uv tool install git+https://github.com/<you>/b1CodingTool
```

**Upgrade after pulling changes:**
```bash
uv tool upgrade b1
# or reinstall from local path after changes:
uv tool install . --force-reinstall
```

**Add a `Makefile` target to make this easy:**
```makefile
install:
	uv tool install . --force-reinstall

uninstall:
	uv tool uninstall b1
```

**Verdict:** This is the right starting point. Zero publishing overhead, works immediately after fixing `requires-python`. Suitable for personal use and sharing with teammates who have uv installed.

---

### Option B — Publish to PyPI

PyPI is the standard Python package index. Publishing here lets anyone install `b1` with:
```bash
uv tool install b1          # preferred
pip install b1              # fallback
```

#### Name Availability

`b1` on PyPI is a very short name and may already be taken or rejected (PyPI reserves names under 3 characters in some cases). Check before committing to the name:

```bash
pip index versions b1       # errors if not found
# or visit: https://pypi.org/project/b1/
```

If `b1` is taken, consider:
- `b1-tool`
- `b1codingtool`
- `b1cli`

The binary name (`b1`) is set independently from the PyPI package name in `pyproject.toml`, so users install `b1-tool` but still type `b1` in the terminal.

#### Steps to Publish

1. **Fix `requires-python`** (see above)
2. **Improve package metadata** in `pyproject.toml`:
   ```toml
   [project]
   name = "b1-tool"        # or b1, pending availability check
   version = "0.1.0"
   description = "AI coding context management tool — scaffolds agent.md hierarchies and syncs modules"
   readme = "README.md"
   license = { text = "MIT" }
   requires-python = ">=3.12"
   keywords = ["cli", "ai", "coding", "agent"]
   classifiers = [
       "Development Status :: 3 - Alpha",
       "Environment :: Console",
       "Intended Audience :: Developers",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.12",
       "Topic :: Software Development :: Libraries :: Application Frameworks",
   ]
   ```
3. **Build:**
   ```bash
   uv build    # produces dist/b1_tool-0.1.0.tar.gz and dist/b1_tool-0.1.0-py3-none-any.whl
   ```
4. **Publish:**
   ```bash
   uv publish  # prompts for PyPI credentials
   ```
5. **Automate with GitHub Actions:** trigger a publish on every git tag (`v*`):

   ```yaml
   # .github/workflows/publish.yml
   name: Publish to PyPI
   on:
     push:
       tags: ["v*"]
   jobs:
     publish:
       runs-on: ubuntu-latest
       environment: pypi
       permissions:
         id-token: write    # OIDC trusted publishing — no API token needed
       steps:
         - uses: actions/checkout@v4
         - uses: astral-sh/setup-uv@v3
         - run: uv build
         - uses: pypa/gh-action-pypi-publish@release/v1
   ```

   Use PyPI's **Trusted Publisher** feature (OIDC) — no API tokens to rotate.

**Verdict:** The right medium-term approach. Gives the project a permanent home and allows anyone to install it with standard tools.

---

### Option C — Homebrew Tap (macOS-First, Most Discoverable)

A Homebrew tap is a GitHub repository named `homebrew-<name>` containing Ruby Formula files. Once created, users install with:

```bash
brew tap brandonlamer-connolly/b1
brew install b1
```

Or in one command:
```bash
brew install brandonlamer-connolly/b1/b1
```

#### Two Formula Approaches

**Approach C1: Python-based formula (simpler to maintain)**

The formula installs the package using Python's `virtualenv_install_with_resources` helper, which Homebrew provides natively for Python tools.

```ruby
# Formula/b1.rb
class B1 < Formula
  desc "AI coding context management tool"
  homepage "https://github.com/brandonlamer-connolly/b1CodingTool"
  url "https://github.com/brandonlamer-connolly/b1CodingTool/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "<sha256 of the tarball>"
  license "MIT"

  depends_on "python@3.12"

  # Generate resource stanzas with:
  # pip3 install homebrew-pypi-poet && poet -f b1-tool
  resource "typer" do
    url "https://files.pythonhosted.org/packages/.../typer-0.x.x.tar.gz"
    sha256 "..."
  end
  # ... repeat for each dependency

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "b1", shell_output("#{bin}/b1 --help")
  end
end
```

Use `homebrew-pypi-poet` to auto-generate the resource stanzas from the installed package.

**Approach C2: Standalone binary formula (no Python dependency)**

Build platform binaries via GitHub Actions (see Option D), then write a formula that downloads the right binary:

```ruby
class B1 < Formula
  desc "AI coding context management tool"
  version "0.1.0"

  on_macos do
    on_arm do
      url "https://github.com/brandonlamer-connolly/b1CodingTool/releases/download/v0.1.0/b1-macos-arm64.tar.gz"
      sha256 "<sha256>"
    end
    on_intel do
      url "https://github.com/brandonlamer-connolly/b1CodingTool/releases/download/v0.1.0/b1-macos-x86_64.tar.gz"
      sha256 "<sha256>"
    end
  end

  def install
    bin.install "b1"
  end

  test do
    assert_match "b1", shell_output("#{bin}/b1 --help")
  end
end
```

C2 is the cleanest user experience (no Python required), but requires the binary build pipeline from Option D.

#### Setting Up the Tap

1. Create a new GitHub repository named exactly `homebrew-b1` (or `homebrew-tap`)
2. Create `Formula/b1.rb` with one of the formulas above
3. Users tap with: `brew tap brandonlamer-connolly/b1`

**Verdict:** The best end-state for a macOS developer tool. Highly discoverable, familiar workflow for Mac developers, no Python knowledge required from users.

---

### Option D — GitHub Releases with Standalone Binaries

Build self-contained executables that bundle the Python interpreter — no Python installation required on the user's machine.

#### Build Tool: PyInstaller

```bash
uv add --dev pyinstaller
uv run pyinstaller --onefile --name b1 src/b1/cli.py
# produces dist/b1 (or dist/b1.exe on Windows)
```

#### GitHub Actions Build Matrix

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: macos-14          # Apple Silicon (arm64)
            artifact: b1-macos-arm64
          - os: macos-13          # Intel (x86_64)
            artifact: b1-macos-x86_64
          - os: ubuntu-latest
            artifact: b1-linux-x86_64
          - os: windows-latest
            artifact: b1-windows-x86_64.exe
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run pyinstaller --onefile --name b1 src/b1/cli.py
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact }}
          path: dist/b1*

  release:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/download-artifact@v4
      - uses: softprops/action-gh-release@v2
        with:
          files: "**/*"
```

#### Install Script (curl | sh)

```bash
# install.sh — hosted at raw.githubusercontent.com/...
#!/bin/sh
set -e
VERSION="0.1.0"
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$ARCH" in
  arm64|aarch64) ARCH="arm64" ;;
  x86_64) ARCH="x86_64" ;;
  *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

URL="https://github.com/brandonlamer-connolly/b1CodingTool/releases/download/v${VERSION}/b1-${PLATFORM}-${ARCH}"
DEST="/usr/local/bin/b1"

echo "Installing b1 ${VERSION}..."
curl -fsSL "$URL" -o "$DEST"
chmod +x "$DEST"
echo "Done. Run: b1 --help"
```

Users install with:
```bash
curl -fsSL https://raw.githubusercontent.com/brandonlamer-connolly/b1CodingTool/main/install.sh | sh
```

**Verdict:** Maximum portability — works on any machine without Python or uv. Pairs perfectly with a Homebrew formula (Option C2). Higher build complexity but a very professional end-user experience.

---

## Recommended Path

### Phase 1 — Works Today (1 hour)

1. **Fix `requires-python`:** change `>=3.14` → `>=3.12` in `pyproject.toml`
2. **Install globally with uv tool:**
   ```bash
   uv tool install .
   b1 --help   # done
   ```
3. Add a `Makefile` with `make install` / `make uninstall` targets for convenience

### Phase 2 — Shareable (1-2 days)

1. Check PyPI name availability for `b1` or `b1-tool`
2. Improve `pyproject.toml` metadata (description, classifiers, license)
3. Publish to PyPI with `uv publish`
4. Set up GitHub Actions trusted publisher for automated PyPI releases on tags

### Phase 3 — Polished (1 week)

1. Add PyInstaller build to GitHub Actions release workflow
2. Create `homebrew-b1` tap repository
3. Write Homebrew formula (Option C2 — binary-based, no Python dependency)
4. Add `install.sh` curl script to the repo
5. Update README with all installation methods

---

## Quick Reference: What Changes in `pyproject.toml`

```toml
[project]
name = "b1"                   # verify availability on PyPI, or use "b1-tool"
version = "0.1.0"
description = "AI coding context management tool"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.12"    # ← CHANGE from >=3.14 (nothing in the code requires 3.14)
keywords = ["cli", "ai", "agent", "coding"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "fastapi>=0.135.3",
    "pydantic>=2.12.5",
    "pyyaml>=6.0.3",
    "rich>=14.3.3",
    "typer>=0.24.1",
    "uvicorn>=0.43.0",
]

[project.scripts]
b1 = "b1.cli:main"            # ← already correct, no change needed

[project.urls]
Homepage = "https://github.com/brandonlamer-connolly/b1CodingTool"
Issues = "https://github.com/brandonlamer-connolly/b1CodingTool/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```
