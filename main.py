import argparse
import os
import requests
import sys
import time
from datetime import datetime

SLACK_PROFILE_URI = 'https://slack.com/api/users.profile'
DEFAULT_SLEEP = 300
DEFAULT_CURRENCY = 'bitcoin'
DEFAULT_EMOJI = ':bitcoin:'


def load_credentials(file):
    """Read in a legacy token"""

    creds_path = file
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


def run(currency, time_interval, emoji):
    token = load_credentials('~/.credentials/slack_legacy_token')

    while True:
        try:
            btc_price = requests.get(f'https://api.coinmarketcap.com/v1/ticker/{currency}').json()[0]['price_usd']
            fmt_price = f'{float(btc_price):.2f}'
            print('{} USD @ {}'.format(
                fmt_price,
                datetime.now()
            ))

            status = {
                'status_text': f'{fmt_price} USD',
                'status_emoji': f'{emoji}',
            }
            set_status(token, status)
        except requests.ConnectionError as e:
            print(e)
            pass

        time.sleep(time_interval)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Select sleep interval and currency to look up.'
    )
    parser.add_argument(
        '--time',
        '-t',
        action='store',
        type=int,
        default=DEFAULT_SLEEP,
        dest='time_interval',
        help='Set the wait period (in seconds) between lookups. Setting this too low (may get you rate limited by the CMC API.',
    )
    parser.add_argument(
        '--currency',
        '-c',
        action='store',
        default=DEFAULT_CURRENCY,
        dest='currency',
        help='Set the currency to look up. This should correspond to a coinmarketcap symbol, e.g. "bitcoin" for https://coinmarketcap.com/currencies/bitcoin/',
    )
    parser.add_argument(
        '--emoji',
        '-e',
        action='store',
        default=DEFAULT_EMOJI,
        dest='emoji',
        help='Set the desired emoji to add to the slack status, if any. e.g. ":bitcoin:" or ":face_horse:"',
    )
    return parser.parse_args(argv[1:])


if __name__ == '__main__':

    args = parse_args(sys.argv)
    run(**vars(args))

