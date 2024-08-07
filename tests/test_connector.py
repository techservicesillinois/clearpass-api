import pytest
from conftest import TEST_DATA, MAC_404


def test_connectivity(cassette, clearpass_client):
    assert clearpass_client.test_connectivity()


def test_failed_connectivity(cassette, clearpass_client):
    result = clearpass_client.test_connectivity()
    assert result is False


def test_disable_mac(cassette, clearpass_client):
    result = clearpass_client.disable_mac_address(**TEST_DATA)
    assert result


def test_404_disable_mac(cassette, clearpass_client):
    '''Test disable on a MAC that is not found.'''
    with pytest.raises(ValueError):
        clearpass_client.disable_mac_address(
            mac=MAC_404,
            disabled_by="TEST",
            reason="THE BEST TEST REASON")


def test_enable_mac(cassette, clearpass_client):
    result = clearpass_client.enable_mac_address(mac=TEST_DATA['mac'])
    assert result


def test_404_enable_mac(cassette, clearpass_client):
    '''Test enable on a MAC that is not found.'''
    with pytest.raises(ValueError):
        clearpass_client.enable_mac_address(mac=MAC_404)


def test_get_info_for_mac_address(cassette, clearpass_client):
    result = clearpass_client.get_info_for_mac_address(mac=TEST_DATA['mac'])
    assert result
