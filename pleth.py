import os
from datetime import datetime

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


def write_plot():

    tracker_data = data.get_data()
    df = pd.DataFrame(tracker_data)
    df.rate = df.rate.round(2)

    # Write csv
    csv_df = df[['codes','confirmed','deaths','recovered']]
    csv_df = csv_df.sort_values(['codes'])
    csv_df.to_csv('data.csv',index=False)

    fig = px.choropleth(df,
        locationmode='USA-states', 
        scope='usa',
        color='rate', 
        locations='codes',
        hover_name='states', 
        hover_data=['confirmed', 'deaths', 'rate'], 
        color_continuous_scale='sunsetdark',)

    total_confirmed = sum(tracker_data['confirmed'])
    total_deaths = sum(tracker_data['deaths'])
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
