#!/usr/bin/env python3
"""Auto-determine semantic version bump by comparing public API against PyPI.

Logic:
  - Installs the current published korea-real-estate from PyPI into a temp dir
  - Extracts public method signatures from old (PyPI) and new (this repo)
  - major: any existing method removed, or existing param removed, or new required param added
  - minor: new public method(s) added (no breaking changes)
  - patch: no public API changes

New version = bump(pypi_version, kind), floored at current pyproject.toml version.

Writes new version to pyproject.toml and korea_realestate/__init__.py in-place.
Prints new version to stdout.

Flags:
  --dry-run   print version but do not update files
"""

import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from email.parser import Parser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT = ROOT / "scripts" / "extract_sigs.py"
CLIENTS = ("PublicDataClient", "RebClient", "JusoClient")


# ---------------------------------------------------------------------------
# Signature extraction
# ---------------------------------------------------------------------------


def extract_sigs(pkg_path: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(EXTRACT), pkg_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Semver comparison
# ---------------------------------------------------------------------------


def compare(old: dict, new: dict) -> str:
    """Return 'major', 'minor', or 'patch'."""
    overall = "patch"
    for cls_name in CLIENTS:
        old_cls = old.get(cls_name) or {}
        new_cls = new.get(cls_name) or {}

        # Removed methods → breaking
        if set(old_cls) - set(new_cls):
            return "major"

        for method in set(old_cls) & set(new_cls):
            old_params = old_cls[method]
            new_params = new_cls[method]
            # Removed params → breaking
            if set(old_params) - set(new_params):
                return "major"
            # New required params → breaking
            for pname in set(new_params) - set(old_params):
                if new_params[pname]["required"]:
                    return "major"

        # New methods → minor
        if set(new_cls) - set(old_cls):
            overall = "minor"

    return overall


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------


def get_pypi_version() -> str | None:
    """Fetch latest published version from PyPI JSON API."""
    try:
        url = "https://pypi.org/pypi/korea-real-estate/json"
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())["info"]["version"]
    except Exception:
        return None


def get_installed_version(tmpdir: str) -> str | None:
    """Read version from .dist-info/METADATA in tmpdir."""
    for meta in Path(tmpdir).glob("*.dist-info/METADATA"):
        msg = Parser().parsestr(meta.read_text(errors="replace"))
        return msg.get("Version")
    return None


def get_repo_version() -> str:
    text = (ROOT / "pyproject.toml").read_text()
    return re.search(r'version\s*=\s*"([^"]+)"', text).group(1)


def semver_tuple(v: str) -> tuple:
    return tuple(map(int, v.split(".")))


def bump(version: str, kind: str) -> str:
    major, minor, patch = semver_tuple(version)
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def update_files(new_ver: str) -> None:
    replacements = [
        (
            ROOT / "pyproject.toml",
            r'(version\s*=\s*")[^"]+(")',
        ),
        (
            ROOT / "korea_realestate" / "__init__.py",
            r'(__version__\s*=\s*")[^"]+(")',
        ),
    ]
    for path, pattern in replacements:
        text = path.read_text()
        updated = re.sub(
            pattern,
            lambda m, v=new_ver: m.group(1) + v + m.group(2),
            text,
            flags=re.MULTILINE,
        )
        path.write_text(updated)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    with tempfile.TemporaryDirectory() as tmpdir:
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "korea-real-estate",
                f"--target={tmpdir}",
                "--quiet",
            ],
            capture_output=True,
        )

        if install.returncode != 0:
            repo_ver = get_repo_version()
            print(f"No PyPI version found — using repo version {repo_ver}", file=sys.stderr)
            print(repo_ver)
            return

        old_sigs = extract_sigs(tmpdir)
        pypi_ver = get_installed_version(tmpdir) or get_pypi_version() or get_repo_version()

    new_sigs = extract_sigs(str(ROOT))
    kind = compare(old_sigs, new_sigs)

    computed = bump(pypi_ver, kind)
    repo_ver = get_repo_version()

    # Respect manual version bumps in pyproject.toml
    new_ver = computed if semver_tuple(computed) >= semver_tuple(repo_ver) else repo_ver

    print(f"PyPI: {pypi_ver}  |  bump: {kind}  |  new: {new_ver}", file=sys.stderr)
    print(new_ver)

    if not dry_run:
        update_files(new_ver)


if __name__ == "__main__":
    main()
