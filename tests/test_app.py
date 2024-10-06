import pytest


def test_unit_dummy():
    assert True


@pytest.mark.integration
def test_integration_dummy():
    assert True


@pytest.mark.e2e
def test_e2e_dummy():
    assert True
