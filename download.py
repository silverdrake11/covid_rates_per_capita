import os
import time
from datetime import datetime

import requests


COMMITS_URL = 'https://api.github.com/repos/silverdrake11/covid_rates_per_capita/commits?page={}&path=data.csv'
CONTENTS_URL = 'https://raw.githubusercontent.com/silverdrake11/covid_rates_per_capita/{}/data.csv'
DIRNAME = 'historical'


def get_commits():
    num_commits = 1 # Initialize
    page_num = 1
    all_commits = []
    while num_commits:
        response = requests.get(COMMITS_URL.format(page_num))
        commits = response.json()
        all_commits.extend(commits)
        num_commits = len(commits)
        page_num += 1
    return all_commits


def get_file_text(sha):
    return requests.get(CONTENTS_URL.format(sha)).text


commits = get_commits()

if not os.path.isdir(DIRNAME):
    os.mkdir(DIRNAME)

for commit in commits:
    sha = commit['sha']
    timestamp = commit['commit']['committer']['date']
    datetime_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    filename = datetime_obj.strftime('%Y-%m-%d-%H-%M.csv')
    filepath = os.path.join(DIRNAME, filename)
    if os.path.isfile(filepath):
        print('{} already exists!'.format(filename))
    else:
        print(filepath)
        with open(filepath, 'w') as fh:
            fh.write(get_file_text(sha))