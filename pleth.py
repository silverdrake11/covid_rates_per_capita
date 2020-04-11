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


TITLE = "US Covid-19 Rates Per Capita"
HTML_TITLE = TITLE + " (Coronavirus)"
DESCRIPTION = "A map tracking the United States confirmed COVID-19 cases. The darker colors correspond to a greater rate per capita measurement."
HOMEPAGE = 'https://us-covid19-per-capita.net'
TEMPLATE_FILENAME = 'template.html'


def get_cur_time():
    return datetime.now(timezone('America/Chicago')).strftime("%a %b %d %-I:%M %p CST")


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
        df = df.append(data.get_wikipedia_df())
    except:
        traceback.print_exc()

    df = df.astype({'confirmed':int, 'deaths':int, 'recovered':int}) # Make sure they are ints

    # Keep rows that are most recent (sort by deaths, if tie then confirmed)
    df = df.sort_values(['deaths', 'confirmed']).drop_duplicates('codes', keep='last')

    return df


def get_plot_html(df, colors_column):

    fig = px.choropleth(df,
        locationmode='USA-states', 
        scope='usa',
        color=colors_column, 
        locations='codes',
        hover_name='states', 
        hover_data=['confirmed', 'deaths', colors_column], 
        color_continuous_scale='sunsetdark',)

    fig.layout.coloraxis.showscale = False
    fig.layout.dragmode = False
    fig.layout.autosize = True
    fig.layout.margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0,
    )

    plot_html = plotly.io.to_html(fig, 
        include_plotlyjs=False, 
        full_html=False, 
        config={'displayModeBar': False})

    # Remove problematic div tag
    soup = BeautifulSoup(plot_html, 'html.parser')
    soup.div.unwrap()
    plot_html = str(soup)

    return plot_html


def write_index_page(df, total_confirmed, total_deaths, time_updated):

    plot_html = get_plot_html(df, 'rate')

    text = open(TEMPLATE_FILENAME).read()
    t = jinja2.Template(text)
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=time_updated,
            title=TITLE,
            html_title=HTML_TITLE,
            description=DESCRIPTION,
            link=HOMEPAGE)

    with open('index.html', 'w') as fh:
        fh.write(rendered)


def write_deaths_page(df, total_confirmed, total_deaths,  time_updated):

    page_filename = 'deaths.html'
    description = 'A map of USA death rates per state population from the Coronavirus (in this case per 100,000 people). Tap or hover to display the numbers.'

    plot_html = get_plot_html(df, 'drate') # Death rate

    # We need to do this b/c it refers to the other template
    template_loader = jinja2.FileSystemLoader(searchpath='./')
    template_env = jinja2.Environment(loader=template_loader)
    t = template_env.get_template('deaths_template.html')

    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=time_updated,
            title=TITLE.replace('Rates', 'Deaths'),
            html_title=HTML_TITLE.replace('Rates', 'Deaths'),
            description=description,
            link=HOMEPAGE + '/' + page_filename)

    with open(page_filename, 'w') as fh:
        fh.write(rendered)


def write_plot():

    df = get_most_recent_df()
    print(df.source.value_counts())

    # Write csv
    csv_df = df[['codes','confirmed','deaths','recovered']]
    csv_df = csv_df.sort_values(['codes'])
    csv_df.to_csv('data.csv',index=False)

    total_confirmed = df.confirmed.sum()
    total_deaths = df.deaths.sum()
    time_updated = get_cur_time()

    write_index_page(df, total_confirmed, total_deaths, time_updated)
    write_deaths_page(df, total_confirmed, total_deaths, time_updated)

    return total_confirmed # Used to check if there's changes in the data


if __name__ == '__main__':
    write_plot()
