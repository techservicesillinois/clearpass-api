from conftest import TEST_DATA

def test_connectivity(cassette, clearpass_client):
    assert clearpass_client.test_connectivity()


def test_failed_connectivity(cassette, clearpass_client):
    result = clearpass_client.test_connectivity()
    assert result is False


def test_disable_mac(cassette, clearpass_client):
    result = clearpass_client.disable_mac_address(mac=TEST_DATA['mac'])
    assert result


def test_enable_mac(cassette, clearpass_client):
    result = clearpass_client.enable_mac_address(mac=TEST_DATA['mac'])
    assert result
