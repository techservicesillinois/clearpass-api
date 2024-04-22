
def test_connectivity(cassette, clearpass_client):
    result = clearpass_client.test_connectivity()
    assert result == True


def test_failed_connectivity(cassette, clearpass_client):
    result = True
    # assert result == False
