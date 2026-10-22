"""scripts/data_bump.py: moving the API to a new internacia-db release."""

import importlib.util
import re
import tomllib
from pathlib import Path

import pytest

from app.config import settings

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("data_bump", REPO / "scripts" / "data_bump.py")
data_bump = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(data_bump)  # type: ignore[union-attr]

OLD_SHA = "a" * 64
NEW_SHA = "b" * 64


def _project(root: Path, changelog: str) -> Path:
    (root / "app").mkdir()
    (root / "Dockerfile").write_text(
        f"ARG INTERNACIA_DB_VERSION=3.0.0\nARG INTERNACIA_DB_SHA256={OLD_SHA}\nFROM scratch\n"
    )
    (root / "pyproject.toml").write_text('[project]\nname = "internacia-api"\nversion = "0.2.0"\n')
    (root / "app" / "config.py").write_text('class Settings:\n    api_version: str = "0.2.0"\n')
    (root / "uv.lock").write_text('[[package]]\nname = "internacia-api"\nversion = "0.2.0"\n')
    (root / "CHANGELOG.md").write_text(changelog)
    return root


RELEASED = "# Changelog\n\n## [Unreleased]\n\n## [0.2.0] - 2026-11-01\n\n- Old.\n"
PENDING_VERSION = (
    "# Changelog\n\n## [Unreleased]\n\n## [0.2.0] - Unreleased\n\nIntro.\n\n### Added\n\n- New.\n\n"
    "## [0.1.0] - 2026-10-01\n\n### Data\n\n- Serves internacia-db 2.0.0.\n"
)
PENDING_UNRELEASED = (
    "# Changelog\n\n## [Unreleased]\n\n### Fixed\n\n- Bug.\n\n## [0.2.0] - 2026-11-01\n"
)


def test_release_when_nothing_is_pending(tmp_path):
    root = _project(tmp_path, RELEASED)
    assert data_bump.bump("3.1.0", NEW_SHA, root, "2026-11-08") == "0.2.1"
    dockerfile = (root / "Dockerfile").read_text()
    assert "ARG INTERNACIA_DB_VERSION=3.1.0\n" in dockerfile and f"SHA256={NEW_SHA}\n" in dockerfile
    assert (root / "CHANGELOG.md").read_text() == (
        "# Changelog\n\n## [Unreleased]\n\n## [0.2.1] - 2026-11-08\n\n### Data\n\n"
        "- Serves internacia-db 3.1.0 (image `0.2.1-db-3.1.0`).\n\n"
        "## [0.2.0] - 2026-11-01\n\n- Old.\n"
    )
    assert 'version = "0.2.1"' in (root / "pyproject.toml").read_text()
    assert 'api_version: str = "0.2.1"' in (root / "app" / "config.py").read_text()
    assert 'version = "0.2.1"' in (root / "uv.lock").read_text()


def test_note_in_the_pending_version(tmp_path):
    root = _project(tmp_path, PENDING_VERSION)
    assert data_bump.bump("3.1.0", NEW_SHA, root, "2026-11-08") is None
    assert data_bump.bump("3.1.1", NEW_SHA, root, "2026-11-09") is None
    assert (root / "CHANGELOG.md").read_text() == (
        "# Changelog\n\n## [Unreleased]\n\n## [0.2.0] - Unreleased\n\n"
        "Intro.\n\n### Added\n\n- New.\n\n"
        "### Data\n\n- Serves internacia-db 3.1.1.\n\n"
        "## [0.1.0] - 2026-10-01\n\n### Data\n\n- Serves internacia-db 2.0.0.\n"
    )
    assert 'version = "0.2.0"' in (root / "pyproject.toml").read_text()


def test_note_in_unreleased(tmp_path):
    root = _project(tmp_path, PENDING_UNRELEASED)
    assert data_bump.bump("3.1.0", NEW_SHA, root, "2026-11-08") is None
    assert (root / "CHANGELOG.md").read_text() == (
        "# Changelog\n\n## [Unreleased]\n\n### Fixed\n\n- Bug.\n\n### Data\n\n"
        "- Serves internacia-db 3.1.0.\n\n## [0.2.0] - 2026-11-01\n"
    )


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = _project(tmp_path, RELEASED)
    monkeypatch.setattr(data_bump, "ROOT", root)
    monkeypatch.setattr(data_bump, "database_sha256", lambda tag: NEW_SHA)
    return root


def _run(monkeypatch, tmp_path_factory, *argv: str) -> dict[str, str]:
    out = tmp_path_factory.mktemp("gh") / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setattr("sys.argv", ["data_bump.py", *argv])
    assert data_bump.main() == 0
    return dict(line.split("=", 1) for line in out.read_text().splitlines())


def test_main_outputs(repo, monkeypatch, tmp_path_factory):
    monkeypatch.setattr(data_bump, "_latest_release_tag", lambda: "v3.0.0")
    assert _run(monkeypatch, tmp_path_factory)["changed"] == "false"

    outputs = _run(
        monkeypatch, tmp_path_factory, "--version", "3.1.0", "--pr-body", str(repo / "b")
    )
    assert outputs == {
        "changed": "true",
        "version": "3.1.0",
        "previous": "3.0.0",
        "auto_merge": "true",
        "api_version": "0.2.1",
    }
    assert "ghcr.io/datenoio/internacia-api:0.2.1-db-3.1.0" in (repo / "b").read_text()


def test_new_contract_major_is_not_auto_merged(repo, monkeypatch, tmp_path_factory):
    outputs = _run(
        monkeypatch, tmp_path_factory, "--version", "4.0.0", "--pr-body", str(repo / "b")
    )
    assert outputs["auto_merge"] == "false"
    assert "Contract major changed" in (repo / "b").read_text()


def test_repository_versions_agree():
    project = tomllib.loads((REPO / "pyproject.toml").read_text())["project"]["version"]
    assert settings.api_version == project
    lock = (REPO / "uv.lock").read_text()
    assert re.search(rf'name = "internacia-api"\nversion = "{re.escape(project)}"', lock)
    assert data_bump.parse_version(data_bump.dockerfile_version(REPO))
