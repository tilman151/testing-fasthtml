import pytest


@pytest.mark.integration
def test_integration_dummy(client):
    assert True


@pytest.mark.e2e
def test_e2e_dummy(server):
    assert True
