"""
Version bump script for CampaignMaster.

Synchronizes versions across pyproject.toml, package.json, and package-lock.json,
and generates changelogs from conventional commits.

Tags and releases are created by CI when version changes are pushed to main.

Usage:
    python packaging/bump_version.py <major|minor|patch> [OPTIONS]
    python packaging/bump_version.py --set <VERSION> [OPTIONS]

Options:
    --set TEXT       Set an exact version (e.g., 2.0.0, 1.5.0-beta.1)
    --pre TEXT       Pre-release label (alpha, beta, rc)
    --finalize       Remove pre-release suffix and finalize version
    --dry-run        Preview changes without writing
    --no-changelog   Skip changelog generation
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, timezone
from enum import Enum
from pathlib import Path

import typer

app = typer.Typer(help="Bump CampaignMaster version across all project files.")

ROOT_DIR = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
PACKAGE_JSON_PATH = ROOT_DIR / "package.json"
PACKAGE_LOCK_PATH = ROOT_DIR / "package-lock.json"
CHANGELOG_PATH = ROOT_DIR / "CHANGELOG.md"


class BumpType(str, Enum):
    major = "major"
    minor = "minor"
    patch = "patch"


# -- Version parsing/formatting --


def parse_version(version_str: str) -> tuple[int, int, int, str | None, int | None]:
    """Parse a semver string into (major, minor, patch, pre_label, pre_number)."""
    match = re.match(
        r"^(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc)\.(\d+))?$",
        version_str,
    )
    if not match:
        typer.echo(f"Error: Could not parse version '{version_str}'", err=True)
        raise typer.Exit(1)
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    pre_label = match.group(4)
    pre_number = int(match.group(5)) if match.group(5) is not None else None
    return major, minor, patch, pre_label, pre_number


def format_version(
    major: int, minor: int, patch: int, pre_label: str | None = None, pre_number: int | None = None
) -> str:
    """Format version components into a semver string."""
    version = f"{major}.{minor}.{patch}"
    if pre_label is not None:
        version += f"-{pre_label}.{pre_number or 1}"
    return version


def compute_new_version(
    current: str,
    bump: BumpType,
    pre: str | None = None,
    finalize: bool = False,
) -> str:
    """Compute the new version string based on bump type and flags."""
    major, minor, patch, cur_pre_label, cur_pre_number = parse_version(current)

    if finalize:
        if cur_pre_label is None:
            typer.echo("Error: --finalize used but current version has no pre-release suffix.", err=True)
            raise typer.Exit(1)
        return format_version(major, minor, patch)

    if pre:
        # If already a pre-release with the same label, increment pre-release number
        if cur_pre_label == pre:
            return format_version(major, minor, patch, pre, (cur_pre_number or 0) + 1)
        # Otherwise, bump the version component first, then apply pre-release
        if bump == BumpType.major:
            return format_version(major + 1, 0, 0, pre, 1)
        elif bump == BumpType.minor:
            return format_version(major, minor + 1, 0, pre, 1)
        else:
            return format_version(major, minor, patch + 1, pre, 1)

    # Standard bump (strip any pre-release suffix)
    if cur_pre_label is not None:
        # Bumping a pre-release without --pre finalizes it at the current level
        return format_version(major, minor, patch)

    if bump == BumpType.major:
        return format_version(major + 1, 0, 0)
    elif bump == BumpType.minor:
        return format_version(major, minor + 1, 0)
    else:
        return format_version(major, minor, patch + 1)


# -- File reading/writing --


def read_current_version() -> str:
    """Read the current version from pyproject.toml (source of truth)."""
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        typer.echo("Error: Could not find version in pyproject.toml", err=True)
        raise typer.Exit(1)
    return match.group(1)


def update_pyproject(new_version: str, dry_run: bool) -> None:
    """Update version in pyproject.toml using regex replacement."""
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    updated = re.sub(
        r'^(version\s*=\s*")[^"]+"',
        rf'\g<1>{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if dry_run:
        typer.echo(f"  [dry-run] Would update pyproject.toml -> {new_version}")
    else:
        PYPROJECT_PATH.write_text(updated, encoding="utf-8")
        typer.echo(f"  Updated pyproject.toml -> {new_version}")


def update_package_json(path: Path, new_version: str, dry_run: bool) -> None:
    """Update version in a package.json or package-lock.json file."""
    if not path.exists():
        typer.echo(f"  Skipped {path.name} (not found)")
        return

    content = path.read_text(encoding="utf-8")
    data = json.loads(content)
    data["version"] = new_version

    # package-lock.json also has a version in packages[""]
    if path.name == "package-lock.json" and "packages" in data and "" in data["packages"]:
        data["packages"][""]["version"] = new_version

    if dry_run:
        typer.echo(f"  [dry-run] Would update {path.name} -> {new_version}")
    else:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"  Updated {path.name} -> {new_version}")


# -- Git helpers --


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result."""
    return subprocess.run(
        ["git", *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=check,
    )


def get_last_version_boundary() -> str | None:
    """Get a git ref for the last version boundary (tag or bump commit).

    Checks for version tags first, then falls back to the most recent
    'Bump version to ...' commit. This prevents changelog duplication
    when tags are created asynchronously by CI.
    """
    # First, try to find the most recent version tag
    tag_result = run_git("tag", "--list", "v*", "--sort=-v:refname", check=False)
    last_tag = None
    if tag_result.returncode == 0 and tag_result.stdout.strip():
        last_tag = tag_result.stdout.strip().splitlines()[0]

    # Also find the most recent "Bump version" commit
    bump_result = run_git("log", "--grep=^Bump version to ", "--pretty=format:%H", "-1", check=False)
    last_bump_commit = None
    if bump_result.returncode == 0 and bump_result.stdout.strip():
        last_bump_commit = bump_result.stdout.strip()

    if last_tag and last_bump_commit:
        # Use whichever is more recent (closer to HEAD)
        merge_base = run_git("merge-base", "--is-ancestor", last_tag, last_bump_commit, check=False)
        if merge_base.returncode == 0:
            # bump commit is at or after the tag -> use bump commit
            return last_bump_commit
        else:
            # tag is after the bump commit -> use tag
            return last_tag
    return last_tag or last_bump_commit


def get_commits_since(ref: str | None) -> list[str]:
    """Get commit messages since the given ref (or all commits if None)."""
    if ref:
        result = run_git("log", f"{ref}..HEAD", "--pretty=format:%s", check=False)
    else:
        result = run_git("log", "--pretty=format:%s", check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return []
    return result.stdout.strip().splitlines()


# -- Changelog --

COMMIT_CATEGORIES = {
    "feat": "Added",
    "fix": "Fixed",
    "refactor": "Changed",
    "docs": "Documentation",
    "perf": "Performance",
    "style": "Changed",
    "build": "Changed",
    "ci": "Changed",
    "test": "Changed",
}

BREAKING_KEYWORDS = ["BREAKING CHANGE", "BREAKING-CHANGE"]


def categorize_commits(messages: list[str]) -> dict[str, list[str]]:
    """Categorize commit messages by conventional commit prefix."""
    categories: dict[str, list[str]] = {}
    for msg in messages:
        # Check for breaking changes
        is_breaking = any(kw in msg for kw in BREAKING_KEYWORDS)
        if is_breaking:
            categories.setdefault("Breaking Changes", []).append(msg)
            continue

        # Match conventional commit pattern: type(scope): description or type: description
        match = re.match(r"^(\w+)(?:\([^)]*\))?:\s*(.+)$", msg)
        if match:
            prefix = match.group(1).lower()
            description = match.group(2).strip()
            category = COMMIT_CATEGORIES.get(prefix, "Other")
            categories.setdefault(category, []).append(description)
        else:
            categories.setdefault("Other", []).append(msg)

    return categories


def generate_changelog_section(version: str, categories: dict[str, list[str]]) -> str:
    """Generate a changelog section for the given version."""
    today = date.today().isoformat()
    lines = [f"## [{version}] - {today}", ""]

    # Order: Breaking Changes first, then alphabetical
    ordered_cats = []
    if "Breaking Changes" in categories:
        ordered_cats.append("Breaking Changes")
    for cat in sorted(categories.keys()):
        if cat != "Breaking Changes":
            ordered_cats.append(cat)

    for cat in ordered_cats:
        lines.append(f"### {cat}")
        lines.append("")
        for entry in categories[cat]:
            lines.append(f"- {entry}")
        lines.append("")

    return "\n".join(lines)


def update_changelog(version: str, categories: dict[str, list[str]], dry_run: bool) -> None:
    """Prepend a new version section to CHANGELOG.md."""
    new_section = generate_changelog_section(version, categories)

    if dry_run:
        typer.echo("  [dry-run] Would update CHANGELOG.md with:")
        typer.echo("")
        for line in new_section.splitlines():
            typer.echo(f"    {line}")
        typer.echo("")
        return

    if CHANGELOG_PATH.exists():
        existing = CHANGELOG_PATH.read_text(encoding="utf-8")
        # Insert after the header line(s)
        header_match = re.match(
            r"(# Changelog\s*\n(?:\s*\n)*)",
            existing,
        )
        if header_match:
            updated = existing[: header_match.end()] + new_section + "\n" + existing[header_match.end() :]
        else:
            updated = new_section + "\n" + existing
    else:
        updated = (
            "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n" + new_section
        )

    CHANGELOG_PATH.write_text(updated, encoding="utf-8")
    typer.echo("  Updated CHANGELOG.md")


# -- Main command --


@app.command()
def bump(
    bump_type: BumpType | None = typer.Argument(None, help="Version component to bump: major, minor, or patch"),
    set_version: str | None = typer.Option(None, "--set", help="Set an exact version (e.g., 2.0.0, 1.5.0-beta.1)"),
    pre: str | None = typer.Option(None, help="Pre-release label (alpha, beta, rc)"),
    finalize: bool = typer.Option(False, "--finalize", help="Remove pre-release suffix"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
    no_changelog: bool = typer.Option(False, "--no-changelog", help="Skip changelog generation"),
) -> None:
    """Bump the project version, update all files, and optionally generate changelog."""
    if set_version and (bump_type or pre or finalize):
        typer.echo("Error: --set cannot be combined with bump_type, --pre, or --finalize", err=True)
        raise typer.Exit(1)

    if not set_version and not bump_type and not finalize:
        typer.echo("Error: Must provide either a bump type (major/minor/patch) or --set VERSION", err=True)
        raise typer.Exit(1)

    if pre and pre not in ("alpha", "beta", "rc"):
        typer.echo("Error: --pre must be one of: alpha, beta, rc", err=True)
        raise typer.Exit(1)

    current_version = read_current_version()

    if set_version:
        # Validate the provided version string by parsing it
        parse_version(set_version)
        new_version = set_version
    else:
        new_version = compute_new_version(current_version, bump_type, pre, finalize)

    typer.echo(f"\nVersion: {current_version} -> {new_version}")

    if not dry_run:
        if not typer.confirm("Proceed?"):
            raise typer.Abort()

    typer.echo("")

    # Generate changelog
    if not no_changelog:
        last_ref = get_last_version_boundary()
        commits = get_commits_since(last_ref)
        if commits:
            categories = categorize_commits(commits)
            update_changelog(new_version, categories, dry_run)
        else:
            typer.echo("  No commits found for changelog.")

    # Update version files
    typer.echo("\nUpdating version files:")
    update_pyproject(new_version, dry_run)
    update_package_json(PACKAGE_JSON_PATH, new_version, dry_run)
    update_package_json(PACKAGE_LOCK_PATH, new_version, dry_run)

    if dry_run:
        typer.echo("\n[dry-run] No files were modified.")
        return

    # Git commit
    files_to_stage = ["pyproject.toml", "package.json", "package-lock.json"]
    if not no_changelog and CHANGELOG_PATH.exists():
        files_to_stage.append("CHANGELOG.md")

    run_git("add", *files_to_stage)
    run_git("commit", "-m", f"Bump version to {new_version}")
    typer.echo(f"\n  Committed: Bump version to {new_version}")

    # Prompt to push
    typer.echo("")
    current_branch = run_git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if typer.confirm(f"Push commit to remote (branch '{current_branch}')?", default=False):
        push_result = run_git("push", "origin", current_branch, check=False)
        if push_result.returncode != 0:
            typer.echo(
                f"\n  Push failed. This may be due to a merge conflict or out-of-date branch.\n"
                f"  Please pull/merge manually and then push:\n\n"
                f"    git pull --rebase origin {current_branch}\n"
                f"    git push origin {current_branch}\n",
                err=True,
            )
            typer.echo(f"  Git output: {push_result.stderr.strip()}", err=True)
            raise typer.Exit(1)
        typer.echo(f"  Pushed to remote branch '{current_branch}'.")

    typer.echo(f"\nDone! Version bumped to {new_version}")


if __name__ == "__main__":
    app()
