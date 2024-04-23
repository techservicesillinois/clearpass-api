import os

import pytest
import vcr

from clearpass.client import APIConnection

# To record, `export VCR_RECORD=True`
VCR_RECORD = "VCR_RECORD" in os.environ


@pytest.fixture
def clearpass_client(monkeypatch) -> APIConnection:
    if not VCR_RECORD:  # Always use cassette values when using cassette
        kwargs = {
            "username": "JOE",
            "password": "NOTAPASSWORD",
            "endpoint": "http://dev.null",
            "clientid": "FAKEID",
            "secret": "NOTASECRET",
        }
    else:
        env_keys = ['username', 'password', 'endpoint', 'clientid', 'secret']
        kwargs = {}

        for key in env_keys:
            env_key = f"CLEARPASS_{key.upper()}"
            kwargs[key] = os.environ.get(env_key, None)
            if not kwargs[key]:
                raise ValueError(f'{env_key} unset or empty with record mode')

    return APIConnection(**kwargs)


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='once' if VCR_RECORD else 'none',
        # TODO: Uncomment with remove_creds from shared repo
        # before_record_request=remove_creds,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )

    # yaml_cleaner = CleanYAMLSerializer()
    # my_vcr.register_serializer("cleanyaml", yaml_cleaner)
    # TODO: Register cleaner functions here:
    # yaml_cleaner.register_cleaner(clean_bad_word)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml') as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
            assert tape.play_count == 1
