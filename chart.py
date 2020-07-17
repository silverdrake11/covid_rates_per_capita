import os
from datetime import datetime, timedelta
from functools import lru_cache

import requests
import pandas as pd
from pytz import timezone

from download import DIRNAME, CSV_FILENAME


MAX_BINS = 10
NUM_DAYS = 7
CHART_CHAR = '-'
REFERENCE_TZ = 'Pacific/Honolulu'
HISTORICAL_URL = 'https://covidtracking.com/api/v1/states/{}/daily.json'


def get_data_per_day_from_ctp(postal_code, column, num_days):
    data = requests.get(HISTORICAL_URL.format(postal_code).lower()).json()
    values = []
    dates = []
    if column == 'deaths':
        select = 'deathIncrease'
    else:
        select = 'positiveIncrease'
    for item in data:
        values.append(item[select])
        date_obj = datetime.strptime(str(item['date']), '%Y%m%d')
        date_obj = date_obj.replace(tzinfo=timezone(REFERENCE_TZ)).date()
        dates.append(date_obj)
    sr = pd.Series(values, index=dates)
    return sr


def get_data_per_day_from_file(postal_code, column, num_days):
    csv_filepath = os.path.join(DIRNAME, CSV_FILENAME)
    df = pd.read_csv(csv_filepath)
    df = df[df['state'] == postal_code]

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.tz_localize('utc').dt.tz_convert(REFERENCE_TZ)
    df['dates'] = df['timestamp'].dt.date
    df = df.sort_values(['dates', column])

    df = df.drop_duplicates('dates', keep='last')
    df = df.set_index(df['dates'])

    sr = df[column].diff()
    return sr

@lru_cache()
def get_last_n(postal_code, column):
    '''Gets last n confirmed cases or deaths for the last number of days'''

    todays_date = datetime.now(timezone(REFERENCE_TZ)).date()
    idx = pd.date_range(todays_date - timedelta(NUM_DAYS), todays_date)

    sr = get_data_per_day_from_file(postal_code, column, NUM_DAYS)
    sr = sr.reindex(idx, fill_value=0)

    if any(sr<0) or postal_code in ['MD']:
        sr = get_data_per_day_from_ctp(postal_code, column, NUM_DAYS)
        sr = sr.reindex(idx, fill_value=0)

    sr = sr.dropna().astype(int)
    return sr


def to_bins(nums, max_bins):
    max_value = max(nums)
    percentages = [num/max_value if (num>0) else 0 for num in nums]
    return [round(percent*max_bins) if percent>0 else 0 for percent in percentages]


def get_ascii(sr):
    dates = [x.date() for x in sr.index.tolist()]
    values = sr.tolist()
    text = '\n'
    binned = to_bins(values, MAX_BINS)
    for num, date, original_value in zip(binned, dates, values):
        if original_value < 0:
            original_value = ''
        text += date.strftime('%-m/%d') + ' '
        text += CHART_CHAR * num
        text += ' ' * (MAX_BINS - num)
        text += ' {}'.format(original_value)
        text += '\n'
    return text.rstrip()


def get_ascii_chart(postal_code, column):
    if column == 'recent':
        column = 'confirmed'
    sr = get_last_n(postal_code, column)
    return get_ascii(sr)

