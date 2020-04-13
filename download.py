import csv
import json
import os
import time
import zipfile
from datetime import datetime
from urllib.request import urlopen


COMMITS_URL = 'https://api.github.com/repos/silverdrake11/covid_rates_per_capita/commits?page={}&path=data.csv&per_page={}'
CONTENTS_URL = 'https://raw.githubusercontent.com/silverdrake11/covid_rates_per_capita/{}/data.csv'
DIRNAME = 'historical'
CSV_FILENAME = 'historical.csv'
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
            pass
            #print('{} already exists'.format(filename))
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
    
    rows = []
    for key in table:
        (state, confirmed, deaths) = key
        timestamp = table[key].strftime('%Y-%m-%d %H:%M')
        rows.append((state, timestamp, confirmed, deaths))

    return rows


def write_final_csv(dirpath, rows):

    output_filepath = os.path.join(dirpath, CSV_FILENAME)

    with open(output_filepath, mode='w') as fh:
        fieldnames = ['state', 'confirmed', 'deaths', 'timestamp']
        csv_writer = csv.writer(fh)
        csv_writer.writerow(fieldnames)
        for row in rows:
            csv_writer.writerow(row)

    print()
    print("OUTPUT: " + os.path.abspath(output_filepath))


def get_state_deaths(row):
    return row[0], row[3]


def is_bad_row(rows, cur_idx):
    '''There are a few edge cases here'''

    if not cur_idx: # First one should not be removed
        return None

    prev_idx = cur_idx - 1
    next_idx = cur_idx + 1

    prev_state, prev_deaths = get_state_deaths(rows[prev_idx])
    cur_state, cur_deaths = get_state_deaths(rows[cur_idx])

    if prev_state == cur_state:
        if prev_deaths > cur_deaths:
            if next_idx < len(rows): # Special case where prev value is bad
                next_state, next_deaths = get_state_deaths(rows[next_idx])
                if next_state == cur_state:
                    if prev_deaths > next_deaths:
                        return prev_idx
            return cur_idx


def print_row(rows, idx, removed):
    text = ' '.join([str(x) for x in rows[idx]])
    if idx == removed:
        text += ' x'
    print(text)


def remove_rows(rows):
    '''
    Remove rows where number of deaths in next row is greater than previous row..
    How did these rows get there? Either the source made a mistake or I made a 
    mistake.
    '''

    rows = sorted(rows)
    num_rows = len(rows)

    to_remove = set()
    for idx in range(num_rows):
        bad_row_idx = is_bad_row(rows, idx)
        if bad_row_idx:
            to_remove.add(bad_row_idx)
            #print()
            #print_row(rows, idx-3, bad_row_idx)
            #print_row(rows, idx-2, bad_row_idx)
            #print_row(rows, idx-1, bad_row_idx)
            #print_row(rows, idx+0, bad_row_idx)
            #print_row(rows, idx+1, bad_row_idx)
            #print_row(rows, idx+2, bad_row_idx)
            #print_row(rows, idx+3, bad_row_idx)
            #print()
                    
    to_keep = [rows[idx] for idx in range(num_rows) if idx not in to_remove]

    print("Removed {} rows!".format(len(to_remove)))

    return to_keep


def download_and_write_historical():
    download_files(DIRNAME)
    rows = read_files(DIRNAME)
    rows = remove_rows(rows)
    rows = remove_rows(rows) # Run twice to catch any consecutive ones
    write_final_csv(DIRNAME, rows)
    csv_filepath = os.path.join(DIRNAME, CSV_FILENAME)
    zipfile.ZipFile('historical.zip', 'w', zipfile.ZIP_DEFLATED).write(csv_filepath)

 
if __name__ == '__main__':
    download_and_write_historical()


