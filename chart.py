import os
from datetime import datetime, timedelta

import pandas as pd
from pytz import timezone

from download import DIRNAME, CSV_FILENAME


MAX_BINS = 10
NUM_DAYS = 7
CHART_CHAR = '-'


def get_last_n(postal_code, column, num_days):
    '''Gets last n confirmed cases or deaths for the last number of days'''

    reference_tz = 'Pacific/Honolulu'
    csv_filepath = os.path.join(DIRNAME, CSV_FILENAME)
    df = pd.read_csv(csv_filepath)
    df = df[df['state'] == postal_code]

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.tz_localize('utc').dt.tz_convert(reference_tz)
    df['dates'] = df['timestamp'].dt.date
    df = df.sort_values(['dates', column])

    df = df.drop_duplicates('dates', keep='last')
    df = df.set_index(df['dates'])

    sr = df[column].diff().dropna().astype(int)
    todays_date = datetime.now(timezone(reference_tz)).date()
    idx = pd.date_range(todays_date - timedelta(NUM_DAYS), todays_date)
    sr = sr.reindex(idx, fill_value=0)

    dates = [x.date() for x in sr.index.tolist()]
    
    return sr.tolist(), dates


def to_bins(nums, max_bins):
    max_value = max(nums)
    percentages = [num/max_value if num else 0 for num in nums]
    return [round(percent*max_bins) if percent>0 else 0 for percent in percentages]


def get_ascii(values, dates):
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
    values, dates = get_last_n(postal_code, column, NUM_DAYS)
    return get_ascii(values, dates)

