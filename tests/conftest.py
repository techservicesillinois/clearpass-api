import json
import os

import pytest
import vcr

from clearpass.client import APIConnection

from vcr_cleaner import CleanYAMLSerializer, clean_if
from vcr_cleaner.cleaners.jwt_token import clean_token


CASSETTE_USERNAME = "JOE"
CASSETTE_PASSWORD = "NOTAPASSWORD"
CASSETTE_ENDPOINT = "cplab.techservices.illinois.edu"
CASSETTE_CLIENT_ID = "FAKEID"
CASSETTE_CLIENT_SECRET = "NOTASECRET"
URL = f"https://{CASSETTE_ENDPOINT}"

# To record, `export VCR_RECORD=True`
VCR_RECORD = "VCR_RECORD" in os.environ


@pytest.fixture
def clearpass_client(monkeypatch) -> APIConnection:
    if not VCR_RECORD:  # Always use cassette values when using cassette
        kwargs = {
            "username": CASSETTE_USERNAME,
            "password": CASSETTE_PASSWORD,
            "endpoint": CASSETTE_ENDPOINT,
            "client_id": CASSETTE_CLIENT_ID,
            "client_secret": CASSETTE_CLIENT_SECRET,
        }
    else:
        env_keys = ['username', 'password', 'endpoint',
                    'client_id', 'client_secret']
        kwargs = {}

        for key in env_keys:
            env_key = f"CLEARPASS_{key.upper()}"
            kwargs[key] = os.environ.get(env_key, None)
            if not kwargs[key]:
                raise ValueError(f'{env_key} unset or empty with record mode')

    return APIConnection(**kwargs)


@clean_if(uri=f"{URL}/api/oauth")
def clean_auth(request, response):
    breakpoint()
    clean_token(request, response)


def remove_creds(request):
    if not request.body:
        return request
    data = json.loads(request.body.decode('utf-8'))

    if 'password' in data:
        data['password'] = CASSETTE_PASSWORD
    if 'username' in data:
        data['username'] = CASSETTE_USERNAME
    if 'client_id' in data:
        data['client_id'] = CASSETTE_CLIENT_ID
    if 'client_secret' in data:
        data['client_secret'] = CASSETTE_CLIENT_SECRET

    request.body = json.dumps(data)
    return request


@pytest.fixture
def cassette(request) -> vcr.cassette.Cassette:
    my_vcr = vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='once' if VCR_RECORD else 'none',
        # TODO: Uncomment with remove_creds from shared repo
        before_record_request=remove_creds,
        filter_headers=[('Authorization', 'Bearer FAKE_TOKEN')],
        match_on=['uri', 'method'],
    )

    yaml_cleaner = CleanYAMLSerializer()
    my_vcr.register_serializer("cleanyaml", yaml_cleaner)
    # TODO: Register cleaner functions here:
    yaml_cleaner.register_cleaner(clean_auth)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml',
                             seralizer='cleanyaml') as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
            assert tape.play_count == 1
