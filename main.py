import os
import json
import requests

SLACK_PROFILE_URI = 'https://slack.com/api/users.profile'


def load_credentials(file):
    """Read in a legacy token"""

    if not os.path.exists(file):
        try:
            creds_path = os.path.expanduser(file)
        except FileNotFoundError:
            return 'Credentials file not found'

    with open(creds_path, 'r') as fp:
        legacy_token = fp.readline()
    return legacy_token


def get_profile(token):
    response = requests.get('{uri}.get?token={token}'.format(
        uri=SLACK_PROFILE_URI,
        token=token
    )).json()
    if not response['ok']:
        raise ValueError('Invalid token')
    return response['profile']


def get_status(token):
    profile = get_profile(token)
    status = {
        'status_text': profile['status_text'],
        'status_emoji': profile['status_emoji'],
    }
    return status


def set_status(token, status):
    assert 'status_text' in status
    assert 'status_emoji' in status

    url = '{uri}.set?token={token}&profile=%7B%22status_text%22%3A%22{status_text}%22%2C%22status_emoji%22%3A%22{status_emoji}%22%7D'.format(
        uri=SLACK_PROFILE_URI,
        token=token,
        **status
    )
    response = requests.get(url)
    if not response.ok:
        raise ValueError('Something went wrong')

    status = {
        'status_text': response.json()['profile']['status_text'],
        'status_emoji': response.json()['profile']['status_emoji'],
    }
    return status




