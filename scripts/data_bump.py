"""Move the API to the newest internacia-db release.

Used by .github/workflows/data-bump.yml (daily, and on the ``internacia-db-release`` dispatch
from internacia-db). It sets ``INTERNACIA_DB_VERSION`` and ``INTERNACIA_DB_SHA256`` in the
Dockerfile, which CI also uses for the smoke tests, and records the data version in the
CHANGELOG:

- if nothing is waiting to be released (``[Unreleased]`` is empty and the newest version is
  dated), it also bumps the API patch version and dates a new entry, so merging the pull request
  tags a release (release-tag.yml) and publishes the image ``<api>-db-<db>``;
- otherwise it notes the data version in the pending entry, and the image ships with the next
  release.

A release with a different contract major is still written so the pull request shows what
fails, but it is not marked for auto-merge.

Usage:
    python scripts/data_bump.py [--version 3.1.0] [--pr-body data-bump.md]
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests
from internacia.contract import SUPPORTED_CONTRACT_MAJOR, parse_contract
from internacia.downloader import (
    DB_FILE,
    DOWNLOAD_URL,
    _fetch_checksums,
    _latest_release_tag,
    parse_version,
    release_tag,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_NOTE = re.compile(r"(?m)^- Serves internacia-db [^\n]*\n")


def database_sha256(tag: str) -> str:
    """The release's SHA-256 of internacia.duckdb: from SHA256SUMS, else by downloading it."""
    checksums = _fetch_checksums(tag)
    if checksums and DB_FILE in checksums:
        return checksums[DB_FILE]
    digest = hashlib.sha256()
    url = DOWNLOAD_URL.format(tag=tag, name=DB_FILE)
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        for chunk in response.iter_content(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def dockerfile_version(root: Path) -> str:
    match = re.search(r"(?m)^ARG INTERNACIA_DB_VERSION=(\S+)$", (root / "Dockerfile").read_text())
    if not match:
        raise SystemExit("ARG INTERNACIA_DB_VERSION not found in the Dockerfile")
    return match.group(1)


def _sub_once(path: Path, pattern: str, replacement: str) -> None:
    text, count = re.subn(pattern, replacement, path.read_text(encoding="utf-8"), count=1)
    if count != 1:
        raise SystemExit(f"{pattern!r} not found in {path}")
    path.write_text(text, encoding="utf-8")


def bump(db_version: str, sha256: str, root: Path, today: str) -> str | None:
    """Write the new data version; return the new API version if this is a release."""
    dockerfile = root / "Dockerfile"
    _sub_once(
        dockerfile,
        r"(?m)^ARG INTERNACIA_DB_VERSION=\S+$",
        f"ARG INTERNACIA_DB_VERSION={db_version}",
    )
    _sub_once(
        dockerfile, r"(?m)^ARG INTERNACIA_DB_SHA256=\S+$", f"ARG INTERNACIA_DB_SHA256={sha256}"
    )

    changelog = root / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    head, _, rest = text.partition("## [Unreleased]\n")
    unreleased, _, after = rest.partition("\n## [")
    after = "## [" + after
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    api_version = re.search(r'(?m)^version = "([^"]+)"', project).group(1)  # type: ignore[union-attr]
    released = re.match(rf"## \[{re.escape(api_version)}\] - \d{{4}}-\d{{2}}-\d{{2}}\n", after)

    if released and not unreleased.strip():
        major, minor, patch = (int(p) for p in api_version.split("."))
        new_version = f"{major}.{minor}.{patch + 1}"
        entry = (
            f"## [{new_version}] - {today}\n\n### Data\n\n"
            f"- Serves internacia-db {db_version} (image `{new_version}-db-{db_version}`).\n\n"
        )
        changelog.write_text(f"{head}## [Unreleased]\n\n{entry}{after}", encoding="utf-8")
        _sub_once(root / "pyproject.toml", r'(?m)^version = "[^"]+"', f'version = "{new_version}"')
        _sub_once(
            root / "app" / "config.py",
            r'(?m)^(    api_version: str = )"[^"]+"',
            rf'\g<1>"{new_version}"',
        )
        lock = root / "uv.lock"
        if lock.exists():
            _sub_once(
                lock, r'(name = "internacia-api"\nversion = )"[^"]+"', rf'\g<1>"{new_version}"'
            )
        return new_version

    note = f"- Serves internacia-db {db_version}.\n"
    if unreleased.strip() or released:
        unreleased = _add_note(unreleased, note)
    else:
        header, _, remainder = after.partition("\n")
        body, sep, older = remainder.partition("\n## [")
        after = f"{header}\n{_add_note(body, note)}" + (f"\n## [{older}" if sep else "")
    changelog.write_text(f"{head}## [Unreleased]\n{unreleased}\n{after}", encoding="utf-8")
    return None


def _add_note(body: str, note: str) -> str:
    """``body`` of a CHANGELOG entry with ``note`` as the only data-version line under ### Data."""
    body = re.sub(r"### Data\n+(?=### |\Z)", "", DATA_NOTE.sub("", body)).strip("\n")
    if "### Data\n\n" in body:
        body = body.replace("### Data\n\n", f"### Data\n\n{note}", 1)
    else:
        body = (f"{body}\n\n" if body else "") + f"### Data\n\n{note}"
    return f"\n{body.rstrip()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", help="internacia-db release (default: the latest)")
    parser.add_argument("--pr-body", type=Path, help="write the pull request body here")
    args = parser.parse_args()

    tag = release_tag(args.version) if args.version else _latest_release_tag()
    version = tag.removeprefix("v")
    current = dockerfile_version(ROOT)
    outputs = {
        "changed": "false",
        "version": version,
        "previous": current,
        "auto_merge": "false",
        "api_version": "",
    }
    new, old = parse_version(version), parse_version(current)
    if new is None or old is None:
        print(f"Unrecognized version: {version!r} or {current!r}", file=sys.stderr)
        return 1
    if new <= old:
        print(f"Already serving internacia-db {current} (latest: {version})")
    else:
        same_major = parse_contract(version)[0] == SUPPORTED_CONTRACT_MAJOR
        api_version = bump(
            version, database_sha256(tag), ROOT, datetime.now(UTC).date().isoformat()
        )
        outputs.update(
            changed="true", auto_merge=str(same_major).lower(), api_version=api_version or ""
        )
        print(
            f"internacia-db {current} -> {version}"
            + (f"; API release {api_version}" if api_version else "")
        )
        if args.pr_body:
            args.pr_body.write_text(
                pr_body(current, version, same_major, api_version), encoding="utf-8"
            )

    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as f:
            f.writelines(f"{key}={value}\n" for key, value in outputs.items())
    return 0


def pr_body(current: str, version: str, same_major: bool, api_version: str | None) -> str:
    lines = [
        f"Serves internacia-db **{version}** (was {current}): the Docker image bakes it in and the "
        "smoke tests run every route against it.",
        "",
        f"Release notes: https://github.com/datenoio/internacia-db/releases/tag/v{version}",
        "",
    ]
    if api_version:
        lines.append(
            f"Merging releases **v{api_version}**: release-tag.yml tags it and docker.yml "
            f"publishes `ghcr.io/datenoio/internacia-api:{api_version}-db-{version}`."
        )
    else:
        lines.append(
            "Unreleased API changes are pending, so the new data ships with the next release."
        )
    lines.append("")
    if same_major:
        lines.append("Same contract major: merges automatically once CI passes.")
    else:
        lines.append(
            f"**Contract major changed** (the SDK supports {SUPPORTED_CONTRACT_MAJOR}.x): "
            "CI is expected to fail until the SDK and the API support it. Not set to auto-merge."
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
