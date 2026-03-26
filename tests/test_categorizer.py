"""Categorizer tests — require a running PostgreSQL instance.
Set DATABASE_URL env var to run these tests.
Skip if no database available."""

import os

import pytest

# Skip all tests in this module if no DATABASE_URL
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping DB tests",
)


@pytest.fixture
async def repo():
    from db.repository import Repository

    r = Repository(os.environ["DATABASE_URL"])
    await r.init()
    yield r
    await r.close()


async def test_exact_match(repo):
    from services.categorizer import categorize

    result = await categorize("lidl", repo)
    assert result is not None
    assert result.category_name == "Продукты"


async def test_case_insensitive(repo):
    from services.categorizer import categorize

    result = await categorize("LIDL", repo)
    assert result is not None
    assert result.category_name == "Продукты"


async def test_unknown_store(repo):
    from services.categorizer import categorize

    result = await categorize("random unknown store", repo)
    assert result is None
