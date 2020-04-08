import csv
import json
import os
import time
from datetime import datetime
from urllib.request import urlopen


COMMITS_URL = 'https://api.github.com/repos/silverdrake11/covid_rates_per_capita/commits?page={}&path=data.csv&per_page={}'
CONTENTS_URL = 'https://raw.githubusercontent.com/silverdrake11/covid_rates_per_capita/{}/data.csv'
DIRNAME = 'historical'
DATETIME_FORMAT = '%Y-%m-%d-%H-%M'


def get_commits():
    page_num = 1
    all_commits = []
    per_page = 100
    num_commits = per_page # Initialize
    while num_commits == per_page:
        text = urlopen(COMMITS_URL.format(page_num, per_page)).read()
        commits = json.loads(text)
        all_commits.extend(commits)
        num_commits = len(commits)
        page_num += 1
    return all_commits


def get_file_bytes(sha):
    return urlopen(CONTENTS_URL.format(sha)).read()


def download_files(dirpath):

    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    commits = get_commits()
    for commit in commits:
        sha = commit['sha']
        timestamp = commit['commit']['committer']['date']
        datetime_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        filename = datetime_obj.strftime(DATETIME_FORMAT + '.csv')
        filepath = os.path.join(dirpath, filename)
        if os.path.isfile(filepath):
            print('{} already exists'.format(filename))
        else:
            print(filepath)
            with open(filepath, 'wb') as fh:
                fh.write(get_file_bytes(sha))


def read_files(dirpath):

    table = {}

    for filename in sorted(os.listdir(dirpath)):

        if len(filename.split('-')) != 5:
            continue

        filepath = os.path.join(dirpath, filename)

        with open(filepath) as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:

                state = row['codes']
                confirmed = int(float(row['confirmed']))
                deaths = int(float(row['deaths']))

                key = (state, confirmed, deaths)

                if key in table:
                    continue

                dt = datetime.strptime(filename.rstrip('.csv'), DATETIME_FORMAT)
                table[key] = dt
    return table


def write_final_csv(dirpath, table):

    output_filepath = os.path.join(dirpath, 'historical.csv')
    with open(output_filepath, mode='w') as fh:

        fieldnames = ['state', 'confirmed', 'deaths', 'timestamp']
        csv_writer = csv.DictWriter(fh, fieldnames=fieldnames)
        csv_writer.writeheader()

        for key in table:

            (state, confirmed, deaths) = key
            timestamp = table[key].strftime('%Y-%m-%d %H:%M')
            row_dict = {'state': state, 
                'confirmed':confirmed, 
                'deaths':deaths, 
                'timestamp': timestamp}
            csv_writer.writerow(row_dict)
    print()
    print("OUTPUT: " + os.path.abspath(output_filepath))


if __name__ == '__main__':
    download_files(DIRNAME)
    table = read_files(DIRNAME)
    write_final_csv(DIRNAME, table)

