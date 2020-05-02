import os
from datetime import datetime, timedelta

import pandas as pd
from pytz import timezone

from download import DIRNAME, CSV_FILENAME


MAX_STARS = 4
NUM_DAYS = 14
CHART_CHAR = '|'


def get_last_n(postal_code, column, num_days):
    '''Gets last n confirmed cases or deaths for the last number of days'''

    reference_tz = 'Pacific/Honolulu'
    csv_filepath = os.path.join(DIRNAME, CSV_FILENAME)
    df = pd.read_csv(csv_filepath)
    df = df[df['state'] == postal_code]
    df = df.sort_values(['timestamp'])

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.tz_localize('utc').dt.tz_convert(reference_tz)
    df['dates'] = df['timestamp'].dt.date

    df = df.drop_duplicates('dates', keep='last')
    df = df.set_index(df['dates'])

    sr = df[column].diff().dropna().astype(int)
    todays_date = datetime.now(timezone(reference_tz)).date()
    idx = pd.date_range(todays_date - timedelta(NUM_DAYS), todays_date - timedelta(1))
    sr = sr.reindex(idx, fill_value=0)
    
    return sr.tolist()


def to_stars(nums, max_stars):
    max_value = max(nums)
    percentages = [num/max_value if num else 0 for num in nums]
    return [round(percent*max_stars) for percent in percentages]


def get_ascii(nums):
    left_pad = '  '
    max_value = max(nums)
    text = '\n' + left_pad
    for height in reversed(range(1, max_value+1)):
        for num in nums:
            if num >= height:
                text += CHART_CHAR
            else:
                text += ' '
        text += '\n' + left_pad
    return text.rstrip()


def get_ascii_chart(postal_code, column):
    nums = get_last_n(postal_code, column, NUM_DAYS)
    stars = to_stars(nums, MAX_STARS)
    return get_ascii(stars)

