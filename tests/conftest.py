import logging
import os

import pytest
import vcr

from vcr_cleaner import CleanYAMLSerializer

# Required pytest plugins
pytest_plugins = ("splunk-soar-connectors")

# To record, `export VCR_RECORD=True`
VCR_RECORD = "VCR_RECORD" in os.environ


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

    yaml_cleaner = CleanYAMLSerializer()
    my_vcr.register_serializer("cleanyaml", yaml_cleaner)
    # TODO: Register cleaner functions here:
    # yaml_cleaner.register_cleaner(clean_bad_word)

    with my_vcr.use_cassette(f'{request.function.__name__}.yaml',
                             serializer="cleanyaml") as tape:
        yield tape
        if my_vcr.record_mode == 'none':  # Tests only valid when not recording
            assert tape.all_played, \
                f"Only played back {len(tape.responses)} responses"
            assert tape.play_count == 1
