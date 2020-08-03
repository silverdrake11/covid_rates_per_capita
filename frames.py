import os
import traceback

import pandas as pd

import data
from chart import get_last_n
from helpers import LOG_DIR
from tables import POP_TABLE, CODES_TABLE


SCALING_FACTOR = {'confirmed':100000, 'deaths':100000, 'recent':100000, 'recentd':100000}
ROUNDING_FACTOR = {'confirmed':0, 'deaths':0, 'recent':0, 'recentd':1}


def df_get_states(row):
  return CODES_TABLE[row['codes']]


def get_rate(df, column):
    return (SCALING_FACTOR[column] * df[column]) / df['pop']


def df_get_recent_cases(row):
    sr = get_last_n(row['codes'], 'confirmed')
    sr = sr.drop(sr.tail(1).index) # Drop last value
    return sr.sum()


def df_get_recent_deaths(row):
    sr = get_last_n(row['codes'], 'deaths')
    sr = sr.drop(sr.tail(1).index) # Drop last value
    return sr.sum()


def add_cols_to_df(df):
    df['states'] = df.apply(df_get_states, axis=1)
    df['pop'] = df['states'].map(POP_TABLE)
    df['rate'] = get_rate(df, 'confirmed')
    df['drate'] = get_rate(df, 'deaths')
    df['recent'] = df.apply(df_get_recent_cases, axis=1)
    df['recentd'] = df.apply(df_get_recent_deaths, axis=1)
    df['rrate'] = get_rate(df, 'recent')
    df['rdrate'] = get_rate(df, 'recentd')
    df.rrate = df.rrate.round(2)
    df.rate = df.rate.round(2)
    df.drate = df.drate.round(2)


def get_current_site_df():
    df = pd.read_csv('data.csv')
    add_cols_to_df(df, 'site')
    return df


def get_most_recent_df():

    df = pd.DataFrame()
    try:
        df = df.append(data.get_arcgis_df())
    except Exception:
        traceback.print_exc()
    try:
        df = df.append(data.get_worldometer_df())
    except Exception:
        traceback.print_exc()
    try: 
        df = df.append(data.get_wikipedia_df())
    except Exception:
        traceback.print_exc()
    try: 
        df = df.append(data.get_bno_df())
    except Exception:
        traceback.print_exc()
    try: 
        df = df.append(data.get_covidtracking_df())
    except Exception:
        traceback.print_exc()

    df = df.astype({'confirmed':int, 'deaths':int, 'recovered':int}) # Make sure they are ints
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    df.to_csv(os.path.join(LOG_DIR, 'debug1.csv'), index=False)

    # Keep rows that are most recent (sort by deaths, if tie then confirmed)
    df = df.sort_values(['deaths', 'confirmed'], ascending=False)
    grouped = df.groupby('codes')
    df = grouped.nth(1) # Second most recent (to reduce errors)
    df = df.reset_index()
    print(df.source.value_counts())

    add_cols_to_df(df)
    df.to_csv(os.path.join(LOG_DIR, 'debug2.csv'), index=False)

    return df
