import os
import pytest
from conftest import TEST_DATA, MAC_404

# NOTE: Each tests cassette must be played in full in order for
# a test to pass. See the assert statements in conftest.py:133.


def test_connectivity(cassette, clearpass_client):
    assert clearpass_client.test_connectivity()


def test_failed_connectivity(cassette, clearpass_client):
    result = clearpass_client.test_connectivity()
    # This cassette is handcrafted. Expect a failure if you use valid
    # credentials. Expect to lock yourself out if you use invalid credentials.
    assert result is False


def test_disable_mac(cassette, clearpass_client):
    clearpass_client.disable_mac_address(**TEST_DATA)


def test_404_disable_mac(cassette, clearpass_client):
    '''Test disable on a MAC that is not found.'''
    with pytest.raises(ValueError):
        clearpass_client.disable_mac_address(
            mac=MAC_404,
            disabled_by="TEST",
            reason="THE BEST TEST REASON")


def test_enable_mac(cassette, clearpass_client):
    clearpass_client.enable_mac_address(mac=TEST_DATA['mac'])


def test_404_enable_mac(cassette, clearpass_client):
    '''Test enable on a MAC that is not found.'''
    with pytest.raises(ValueError):
        clearpass_client.enable_mac_address(mac=MAC_404)


def test_get_info_for_mac_address(cassette, clearpass_client):
    result = clearpass_client.get_info_for_mac_address(mac=TEST_DATA['mac'])

    assert 'id' in result['endpointinfo'][0]
    assert 'mac_address' in result['endpointinfo'][0]
    assert 'status' in result['endpointinfo'][0]
    assert result['endpointinfo'][0]['mac_address'] == TEST_DATA['mac']
    assert result['endpointinfo'][0]['status'] == 'Disabled'


def test_disconnect_mac_address(cassette, clearpass_client):
    count = clearpass_client.disconnect_mac_address(
        mac=os.environ.get("CLEARPASS_MAC", TEST_DATA['mac']))
    assert count == 1


def test_disconnect_mac_not_found(cassette, clearpass_client):
    count = clearpass_client.disconnect_mac_address(
        mac=os.environ.get("CLEARPASS_MAC", TEST_DATA['mac']))
    assert count == 0
