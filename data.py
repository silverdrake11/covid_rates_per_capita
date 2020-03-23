import csv
import json
from datetime import datetime, timedelta

import requests

from tables import POP_TABLE, STATE_TABLE


DATA_FILENAME = 'data.json'


def get_rate(confirmed, state):
    pop = POP_TABLE[state]
    return 10000 * confirmed/pop


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


def get_john_hopkins_data():

    csvfile = request_john_hopkins().splitlines()

    output = {
        'rate': [],
        'states': [],
        'codes': [],
        'confirmed': [],
        'deaths': [],
        'recovered': []
    }
    
    spamreader = csv.reader(csvfile)
    for row in spamreader:
        if row[1] == 'US':

            state = row[0]
            confirmed = int(row[3])
            deaths = int(row[4])
            recovered = int(row[5])

            if state not in STATE_TABLE:
                print(state)
                break

            output['confirmed'].append(confirmed)
            output['rate'].append(get_rate(confirmed, state))

            output['deaths'].append(deaths)
            output['recovered'].append(recovered)

            output['states'].append(state)
            output['codes'].append(STATE_TABLE[state]) # This is the state abbreviation

    return output


def request_arcgis():
    url = 'https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Z7biAeD8PAkqgmWhxG2A/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)%20AND%20(Country_Region%3D%27US%27)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=250&cacheHint=true'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
        'Origin': 'https://www.arcgis.com',
        'Referer': 'https://www.arcgis.com/apps/opsdashboard/index.html',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'TE': 'Trailers',
    }

    response = requests.get(url, headers=headers)
    with open(DATA_FILENAME, 'w') as fh:
        fh.write(response.text)

    return json.load(open(DATA_FILENAME))


def get_data():

    output = {
        'rate': [],
        'states': [],
        'codes': [],
        'confirmed': [],
        'deaths': [],
        'recovered': []
    }

    items = request_arcgis()

    for item in items['features']:
        details = item['attributes']
        state = details['Province_State']
        if state not in STATE_TABLE:
            print(state)
            break
        
        confirmed = details['Confirmed']
        output['confirmed'].append(confirmed)
        output['rate'].append(get_rate(confirmed, state))

        output['deaths'].append(details['Deaths'])
        output['recovered'].append(details['Recovered'])

        output['states'].append(state)
        output['codes'].append(STATE_TABLE[state]) # This is the state abbreviation

    return output
