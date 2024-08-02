from conftest import TEST_DATA


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
    result = clearpass_client.disable_mac_address(**TEST_DATA)
    # TODO: Update to expect 404 error
    assert result


def test_enable_mac(cassette, clearpass_client):
    result = clearpass_client.enable_mac_address(
        mac=TEST_DATA['mac'],
        mac_id=TEST_DATA['mac_id'])
    assert result


def test_404_enable_mac(cassette, clearpass_client):
    '''Test enable on a MAC that is not found.'''
    result = clearpass_client.enable_mac_address(
        mac=TEST_DATA['mac'],
        mac_id=TEST_DATA['mac_id'])
    # TODO: Update to expect 404 error
    assert result
