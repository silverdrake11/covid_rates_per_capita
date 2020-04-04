import csv
import json
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

from tables import POP_TABLE, STATE_TABLE


DATA_FILENAME = 'data.json'
CODES_TABLE = {v: k for k, v in STATE_TABLE.items()}


def get_rate(confirmed, state):
    pop = POP_TABLE[state]
    return (10000 * confirmed)/pop


def request_john_hopkins():
    today = datetime.now()
    timestamp_format = '%m-%d-%Y'
    today_timestamp = today.strftime(timestamp_format)
    yesterday_timestamp = (today - timedelta(days=1)).strftime(timestamp_format)
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv"
    response = requests.get(url.format(today_timestamp))
    if response.status_code == 200:
        return response.text
    else:
        return requests.get(url.format(yesterday_timestamp)).text


class Output:
    '''Keeps track of the data output format'''

    def __init__(self):

        # This is how plotly / pandas wants it
        self.output = {
            'codes': [],
            'confirmed': [],
            'deaths': [],
            'recovered': [],}

    def add_row(self, state, confirmed, deaths, recovered):

        self.output['confirmed'].append(confirmed)
        self.output['deaths'].append(deaths)
        self.output['recovered'].append(recovered)
        self.output['codes'].append(STATE_TABLE[state]) # This is the state abbreviation

    def get_df(self, source):
        df = pd.DataFrame(self.output)
        add_cols_to_df(df, source)
        return df


def clean_num(num_str):
    num_str = num_str.strip().replace(',','')
    if num_str:
        return int(num_str)
    else:
        return 0


def get_worldometer_df():

    url = 'https://www.worldometers.info/coronavirus/country/us/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id':'usa_table_countries_today'})

    output = Output()

    for tbody in table.findAll('tbody'):
        for item in tbody.findAll('tr'):

            row = item.findAll('td')
            state = row[0].text.strip()
            state = state.title()
            if 'Virgin Islands' in state:
                state = 'Virgin Islands'

            if state not in STATE_TABLE:
                print(state)
                continue

            confirmed = clean_num(row[1].text)
            deaths = clean_num(row[3].text)
            recovered = 0 # Will fill in later

            output.add_row(state, confirmed, deaths, recovered)

    return output.get_df('worldometer') 


def get_john_hopkins_df():

    csvfile = request_john_hopkins().splitlines()

    output = Output()
    
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        if row[1] == 'US':

            state = row[0].title()
            confirmed = int(row[3])
            deaths = int(row[4])
            recovered = int(row[5])

            if state not in STATE_TABLE:
                print(state)
                continue

            output.add_row(state, confirmed, deaths, recovered)

    return output.get_df('jhu') 


def request_arcgis():
    url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/3/query?f=json&where=Country_Region%3D%27US%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&outSR=102100&resultOffset=0&resultRecordCount=75&cacheHint=true'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Origin': 'https://gisanddata.maps.arcgis.com',
        'Referer': 'https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'TE': 'Trailers',
    }

    response = requests.get(url, headers=headers)
    with open(DATA_FILENAME, 'w') as fh:
        fh.write(response.text)

    return json.load(open(DATA_FILENAME))


def get_arcgis_df():

    output = Output()

    items = request_arcgis()

    for item in items['features']:
        details = item['attributes']
        state = details['Province_State']
        state = state.title()

        if state not in STATE_TABLE or state not in POP_TABLE:
            print(state)
            continue
        
        confirmed = details['Confirmed']
        deaths = details['Deaths']
        recovered = details['Recovered']

        output.add_row(state, confirmed, deaths, recovered)

    return output.get_df('arcgis')


def df_get_states(row):
  return CODES_TABLE[row['codes']]

def df_get_rate(row):
    return get_rate(row['confirmed'], row['states'])

def df_get_death_rate(row):
    return get_rate(row['deaths'], row['states'])


def add_cols_to_df(df, source):
    df['source'] = source
    df['states'] = df.apply(df_get_states, axis=1)
    df['rate'] = df.apply(df_get_rate, axis=1)
    df['drate'] = df.apply(df_get_death_rate, axis=1)
    df.rate = df.rate.round(2)
    df.drate = df.drate * 10
    df.drate = df.drate.round(2)


def get_current_site_df():
    df = pd.read_csv('data.csv')
    add_cols_to_df(df, 'site')
    return df





