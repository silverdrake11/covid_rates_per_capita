import os
from datetime import datetime
import traceback

import jinja2
import pandas as pd
import plotly
import plotly.express as px
from bs4 import BeautifulSoup
from pytz import timezone

import data


PLOT_TITLE = "US Covid-19 Rates Per Capita   Confirmed {:,}   Deaths {:,}   Updated {}"
HTML_TITLE = "US Covid-19 Rates Per Capita (Coronavirus)"
DESCRIPTION = "A map of United States confirmed COVID-19 cases. The darker colors correspond to a rate per capita measurement."


def get_cur_time():
    return datetime.now(timezone('America/Chicago')).strftime("%a %b %d %-I:%M %p CST")


def format_html(plot_html, total_confirmed):
    soup = BeautifulSoup(plot_html, 'html.parser')
    soup.div.unwrap()
    plot_html = str(soup)
    text = open('template.html').read()
    t = jinja2.Template(text)
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            title=HTML_TITLE,
            description=DESCRIPTION)
    return rendered


def get_most_recent_df():

    df = pd.DataFrame()
    try:
        df = df.append(data.get_arcgis_df())
    except:
        traceback.print_exc()
    try:
        df = df.append(data.get_worldometer_df())
    except:
        traceback.print_exc()
    try: # In case the data we already have is most recent (for example if the other sources break)
        df = df.append(data.get_current_site_df())
    except:
        traceback.print_exc()

    df = df.astype({'confirmed':int, 'deaths':int, 'recovered':int}) # Make sure they are ints

    # Keep rows that are most recent (sort by deaths, if tie then confirmed)
    df = df.sort_values(['deaths', 'confirmed']).drop_duplicates('codes', keep='last')

    return df


def write_plot():

    df = get_most_recent_df()
    print(df.source.value_counts())

    # Write csv
    csv_df = df[['codes','confirmed','deaths','recovered']]
    csv_df = csv_df.sort_values(['codes'])
    csv_df.to_csv('data.csv',index=False)

    fig = px.choropleth(df,
        locationmode='USA-states', 
        scope='usa',
        color='drate', 
        locations='codes',
        hover_name='states', 
        hover_data=['confirmed', 'deaths', 'drate'], 
        color_continuous_scale='sunsetdark',)

    total_confirmed = df.confirmed.sum()
    total_deaths = df.deaths.sum()
    time_updated = get_cur_time()
    fig.layout.title = PLOT_TITLE.format(total_confirmed, total_deaths, time_updated)

    fig.layout.coloraxis.showscale = False
    fig.layout.dragmode = False

    plot_html = plotly.io.to_html(fig, 
        include_plotlyjs=False, 
        full_html=False, 
        config={'displayModeBar': False})

    plot_html = format_html(plot_html, total_confirmed)

    with open('index.html', 'w') as fh:
        fh.write(plot_html)

    return total_confirmed # Used to check if there's changes in the data


if __name__ == '__main__':
    write_plot()
