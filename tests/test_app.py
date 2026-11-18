"""Small local checks for the validation and Flask routes."""

from unittest.mock import Mock

import pytest

from app import app, add_with_soap


def test_add_with_soap_returns_native_data() -> None:
    """A mocked Zeep response keeps this check independent of the public service."""
    fake_client = Mock()
    fake_client.service.AddInteger.return_value = 42

    result = add_with_soap(7, 35, soap_client=fake_client)

    assert result["result"] == 42
    fake_client.service.AddInteger.assert_called_once_with(Arg1=7, Arg2=35)


def test_get_rejects_out_of_range_number() -> None:
    """The required range validation should return a useful client error."""
    client = app.test_client()
    response = client.get("/add?arg1=10001&arg2=1")

    assert response.status_code == 400
    assert "must be between" in response.get_json()["error"]


def test_rejects_invalid_soap_result() -> None:
    """A response outside the expected result range becomes a clear service error."""
    fake_client = Mock()
    fake_client.service.AddInteger.return_value = 30_000

    with pytest.raises(RuntimeError, match="response validation failed"):
        add_with_soap(7, 35, soap_client=fake_client)


def test_post_requires_json_object() -> None:
    """POST must reject a request that is not the expected JSON object."""
    client = app.test_client()
    response = client.post("/add", data="not json", content_type="text/plain")

    assert response.status_code == 400
    assert "JSON object" in response.get_json()["error"]
