"""Tests for international block-related endpoints."""

from unittest.mock import Mock

from fastapi.testclient import TestClient


def test_get_block_by_id_success(client: TestClient, mock_client: Mock):
    """Test getting a block by ID successfully."""
    mock_block_data = {
        "id": "EU",
        "name": "European Union",
        "blocktype": ["economic", "political"]
    }

    mock_client.intblocks.get_by_id = Mock(return_value=mock_block_data)

    response = client.get("/blocks/EU")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == "EU"
    assert data["data"]["name"] == "European Union"


def test_get_block_not_found(client: TestClient, mock_client: Mock):
    """Test getting a block that doesn't exist."""
    mock_client.intblocks.get_by_id = Mock(return_value=None)

    response = client.get("/blocks/INVALID")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "International block 'INVALID' not found" in data["error"]


def test_get_block_sdk_error(client: TestClient, mock_client: Mock):
    """Test getting a block when SDK raises an error."""
    mock_client.intblocks.get_by_id = Mock(side_effect=Exception("SDK error"))

    response = client.get("/blocks/EU")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_list_blocks_success(client: TestClient, mock_client: Mock):
    """Test listing all blocks successfully."""
    mock_blocks = [
        {"id": "EU", "name": "European Union"},
        {"id": "NATO", "name": "North Atlantic Treaty Organization"}
    ]

    mock_client.intblocks.get_all = Mock(return_value=mock_blocks)

    response = client.get("/blocks")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 2
    assert data["count"] == 2


def test_list_blocks_with_limit(client: TestClient, mock_client: Mock):
    """Test listing blocks with limit."""
    mock_blocks = [{"id": "EU", "name": "European Union"}]

    mock_client.intblocks.get_all = Mock(return_value=mock_blocks)

    response = client.get("/blocks?limit=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    mock_client.intblocks.get_all.assert_called_once_with(limit=1)


def test_list_blocks_empty(client: TestClient, mock_client: Mock):
    """Test listing blocks when no blocks are available."""
    mock_client.intblocks.get_all = Mock(return_value=[])

    response = client.get("/blocks")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "count" in data
    assert len(data["items"]) == 0
    assert data["count"] == 0


def test_get_blocks_by_type(client: TestClient, mock_client: Mock):
    """Test getting blocks by type."""
    mock_blocks = [{"id": "EU", "name": "European Union", "blocktype": ["economic"]}]

    mock_client.intblocks.get_by_blocktype = Mock(return_value=mock_blocks)

    response = client.get("/blocks/type/economic")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_status(client: TestClient, mock_client: Mock):
    """Test getting blocks by status."""
    mock_blocks = [{"id": "EU", "name": "European Union", "status": "formal"}]

    mock_client.intblocks.get_by_status = Mock(return_value=mock_blocks)

    response = client.get("/blocks/status/formal")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_geographic_scope(client: TestClient, mock_client: Mock):
    """Test getting blocks by geographic scope."""
    mock_blocks = [{"id": "UN", "name": "United Nations", "geographic_scope": "global"}]

    mock_client.intblocks.get_by_geographic_scope = Mock(return_value=mock_blocks)

    response = client.get("/blocks/scope/global")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_member(client: TestClient, mock_client: Mock):
    """Test getting blocks by member country."""
    mock_blocks = [{"id": "EU", "name": "European Union"}]

    mock_client.intblocks.get_by_member = Mock(return_value=mock_blocks)

    response = client.get("/blocks/member/US")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_acronym(client: TestClient, mock_client: Mock):
    """Test getting blocks by acronym."""
    mock_blocks = [{"id": "EU", "name": "European Union"}]

    mock_client.intblocks.get_by_acronym = Mock(return_value=mock_blocks)

    response = client.get("/blocks/acronym/EU")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_tag(client: TestClient, mock_client: Mock):
    """Test getting blocks by tag."""
    mock_blocks = [{"id": "EU", "name": "European Union", "tags": ["trade"]}]

    mock_client.intblocks.get_by_tag = Mock(return_value=mock_blocks)

    response = client.get("/blocks/tag/trade")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_topic(client: TestClient, mock_client: Mock):
    """Test getting blocks by topic."""
    mock_blocks = [{"id": "EU", "name": "European Union"}]

    mock_client.intblocks.get_by_topic = Mock(return_value=mock_blocks)

    response = client.get("/blocks/topic/economy")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_by_founded_year(client: TestClient, mock_client: Mock):
    """Test getting blocks by founded year."""
    mock_blocks = [{"id": "EU", "name": "European Union", "founded": "1993"}]

    mock_client.intblocks.get_by_founded_year = Mock(return_value=mock_blocks)

    response = client.get("/blocks/founded/1993")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1


def test_get_blocks_count(client: TestClient, mock_client: Mock):
    """Test getting blocks count."""
    mock_client.intblocks.count = Mock(return_value=50)

    response = client.get("/blocks/count")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 50
