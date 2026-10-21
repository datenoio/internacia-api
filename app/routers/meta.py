"""Data version and contract endpoint."""

from importlib.metadata import version as package_version

from fastapi import APIRouter

from app.config import settings
from app.dependencies import InternaciaClientDep

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("")
def get_meta(client: InternaciaClientDep):
    """
    Versions of the API, the SDK and the internacia-db data being served.

    `data` comes from the database's `_meta` table: `version`, `contract_version`,
    `build_date`, `git_commit`, `data_license` and per-dataset `row_count` and `schema_hash`.
    """
    return {
        "api_version": settings.api_version,
        "sdk_version": package_version("internacia"),
        "data": client.meta(),
    }
