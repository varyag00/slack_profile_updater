import pytest
import main

@pytest.fixture
def token():
    return main.load_credentials('~/.credentials/slack_agl_legacy_token')


def test_load_credentials():
    token = main.load_credentials('~/.credentials/slack_agl_legacy_token')
    assert token is not None


def test_get_profile(token):
    profile = main.get_profile(token)
    assert profile is not None


def test_get_status(token):
    status = main.get_status(token)
    assert status is not None

def test_set_profile(token):
    """set it and then reset it to its current value"""
    original = main.get_status(token)

    new = {
        'status_text': original['status_text'] + '!',
        'status_emoji': original['status_emoji'],
    }
    expected = main.set_status(token, new)

    assert new == expected
    assert main.get_status(token) == expected

