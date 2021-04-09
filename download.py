import csv
import json
import os
import time
import zipfile
from datetime import datetime
from urllib.request import urlopen

from helpers import STATIC_DIR


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
        if page_num > 10: # To prevent rate limits
            break
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
        fieldnames = ['state', 'timestamp', 'confirmed', 'deaths']
        csv_writer = csv.writer(fh)
        csv_writer.writerow(fieldnames)
        for row in rows:
            csv_writer.writerow(row)

    print("OUTPUT: " + os.path.abspath(output_filepath))


def test_func(row): # Sort by deaths, confirmed instead of by date (as some data is out of order)
    row = list(row)
    row[1] = row[1].split()[0]
    return row[0],row[1],row[3],row[2]


def reversed_bisect_right(a, x):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if x > a[mid]: 
            hi = mid
        else: 
            lo = mid+1
    return lo


def lis(rows, row_idx):
    '''Longest Increasing Subsquence (Reversed)'''
    rows = list(reversed(rows))
    nums = [row[row_idx] for row in rows]
    tails = []
    indices = []
    table = {}
    for i, num in enumerate(nums):
        pile = reversed_bisect_right(tails, num)
        if pile == len(tails):
            tails.append(num)
            indices.append(i)
        else:
            tails[pile] = num
            indices[pile] = i
        if pile:
            table[i] = indices[pile-1]
        else:
            table[i] = None
    values = []
    cur = indices[-1]
    while cur is not None:
        values.append(rows[cur])
        cur = table[cur]
    return values


def process_state(rows):
    state = rows[0][0]
    num_rows = len(rows)
    rows = lis(rows,-1)
    rows = lis(rows,-2)
    removed = num_rows - len(rows)
    return rows,removed


def remove_rows(rows):
    rows = sorted(rows,key=test_func)
    num_rows = len(rows)
    state_rows = []
    state = rows[0][0]
    tally = 0
    rows_to_keep = []
    for row in rows:
        cur_state = row[0]
        if cur_state == state:
            state_rows.append(row)
        else:
            filtered_state, num_removed = process_state(state_rows)
            rows_to_keep.extend(filtered_state)
            tally += num_removed
            state_rows = []
        state = cur_state
    print("Removed {} rows!".format(tally))
    return rows_to_keep


def download_and_write_historical():
    if not os.path.isdir(DIRNAME):
        os.mkdir(DIRNAME)
    download_files(DIRNAME)
    rows = read_files(DIRNAME)
    rows = remove_rows(rows)
    write_final_csv(DIRNAME, rows)
    csv_filepath = os.path.join(DIRNAME, CSV_FILENAME)
    if not os.path.isdir(STATIC_DIR):
        os.mkdir(STATIC_DIR)
    zip_filename = os.path.join(STATIC_DIR, 'historical.zip')
    zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED).write(csv_filepath)

 
if __name__ == '__main__':
    download_and_write_historical()
