import time

import requests
from datetime import date, timedelta
from retrying import retry

from helpers import get_confirmed, format_time


ALERTS = []
URL = 'https://api.github.com/repos/silverdrake11/covid_rates_per_capita/issues/2/comments'
CREDENTIALS_FILENAME = 'credentials.txt'


def alert(*stuff):
    ALERTS.append(','.join(map(str, stuff)))


def get_credentials():
    with open(CREDENTIALS_FILENAME) as fh:
        return fh.read().split(':')[1].strip('/')


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
def get_comments():
    date_str = (date.today() - timedelta(1)).isoformat()
    url = URL + '?since={}'.format(date_str)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=3)
def post_comment(credentials, comment):
    response = requests.post(URL, 
            headers={'Authorization': 'token ' + credentials}, 
            json={'body':comment})
    response.raise_for_status()


def post_alerts():
    old_alerts = []
    comments = get_comments()
    for comment in comments:
        old_alerts.extend(comment['body'].splitlines())
    old_alerts = set(old_alerts)
    to_post = []
    for alert in set(ALERTS):
        if alert not in old_alerts:
            to_post.append(alert)
    credentials = get_credentials()
    if to_post:
        post_comment(credentials, '\n'.join(to_post))


if __name__ == '__main__':
    prev_label = None
    credentials = get_credentials()
    while True:
        try:
            label = get_confirmed()
            if label == prev_label:
                try:
                    post_comment(credentials, 'SITE DOWN!')
                except:
                    traceback.print_exc()
            prev_label = label
        except:
            traceback.print_exc()
        print(format_time(get_cur_time()))
        time.sleep(7200)
