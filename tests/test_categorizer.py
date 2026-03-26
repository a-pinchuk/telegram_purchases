import pytest
import pytest_asyncio

from db.repository import Repository
from services.categorizer import categorize


@pytest_asyncio.fixture
async def repo(tmp_path):
    r = Repository(str(tmp_path / "test.db"))
    await r.init()
    yield r
    await r.close()


@pytest.mark.asyncio
async def test_exact_match(repo):
    result = await categorize("lidl", repo)
    assert result is not None
    assert result.category_name == "Продукты"


@pytest.mark.asyncio
async def test_case_insensitive(repo):
    result = await categorize("LIDL", repo)
    assert result is not None
    assert result.category_name == "Продукты"


@pytest.mark.asyncio
async def test_leroy_merlin(repo):
    result = await categorize("leroy merlin", repo)
    assert result is not None
    assert result.category_name == "Бытовые товары"


@pytest.mark.asyncio
async def test_unknown_store(repo):
    result = await categorize("random unknown store", repo)
    assert result is None


@pytest.mark.asyncio
async def test_empty_description(repo):
    result = await categorize("", repo)
    assert result is None


@pytest.mark.asyncio
async def test_substring_match(repo):
    result = await categorize("lidl express", repo)
    assert result is not None
    assert result.category_name == "Продукты"
