"""Download a pinned internacia-db release DuckDB file for the smoke tests.

Usage:
    python scripts/fetch_test_db.py --version 3.0.0 --sha256 <hex> \
        --output .test-data/internacia.duckdb

The file is fetched from the GitHub Release asset URL directly (no GitHub API
call, so no rate limit) and verified against the expected SHA-256. An existing
file with the right checksum is reused.
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

RELEASE_URL = (
    "https://github.com/datenoio/internacia-db/releases/download/v{version}/internacia.duckdb"
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", required=True, help="internacia-db release, e.g. 3.0.0")
    parser.add_argument("--sha256", required=True, help="expected SHA-256 of internacia.duckdb")
    parser.add_argument("--output", required=True, type=Path, help="destination file path")
    args = parser.parse_args()

    output: Path = args.output
    expected = args.sha256.lower()

    if output.exists() and sha256_of(output) == expected:
        print(f"{output} already matches {expected}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    url = RELEASE_URL.format(version=args.version)
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as response, tmp.open("wb") as f:  # noqa: S310
        while chunk := response.read(1 << 20):
            f.write(chunk)

    actual = sha256_of(tmp)
    if actual != expected:
        tmp.unlink()
        print(f"SHA-256 mismatch for {url}: expected {expected}, got {actual}", file=sys.stderr)
        return 1

    tmp.replace(output)
    print(f"Saved {output} ({output.stat().st_size} bytes, sha256 {actual})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
