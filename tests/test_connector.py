
def test_connectivity(cassette, clearpass_client):
    assert clearpass_client.test_connectivity()


def test_failed_connectivity(cassette, clearpass_client):
    result = True
    # assert result == False
