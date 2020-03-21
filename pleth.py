import os
from datetime import datetime

import jinja2
import pandas as pd
import plotly
import plotly.express as px
from bs4 import BeautifulSoup
from pytz import timezone

from data import get_data


TITLE = "US Covid-19 Rates Per Capita   Confirmed {}   Deaths {}   Updated {}"


def get_cur_time():
    return datetime.now(timezone('America/Chicago')).strftime("%a %b %d %H:%M %p CST")


def format_html(plot_html, total_confirmed):
    '''text = open('file.html').read()
    t = jinja2.Template(text)
    rendered = t.render(plot=hello)'''
    plot_html = '<!DOCTYPE html>' + plot_html
    soup = BeautifulSoup(plot_html, 'html.parser')
    soup.body.div.unwrap()
    soup.html.attrs['style'] = 'height:100%; width=200%;'
    soup.body.attrs['style'] = 'height:100%; width=200%;'
    soup.body.attrs['data-total'] = total_confirmed

    script = soup.new_tag('script')
    script.attrs['async'] = None
    script.attrs['src'] = 'https://www.googletagmanager.com/gtag/js?id=UA-161455592-1'
    soup.head.append(script)

    script = soup.new_tag('script')
    script.string = '''
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'UA-161455592-1');
    '''
    soup.head.append(script)

    script = soup.new_tag('script')
    script.attrs['src'] = 'https://cdn.plot.ly/plotly-latest.min.js'
    soup.head.append(script)
    
    return str(soup)


def write_plot():

    tracker_data = get_data()
    df = pd.DataFrame(tracker_data)
    df.rate = df.rate.round(2)

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
    fig.layout.title = TITLE.format(total_confirmed, total_deaths, time_updated)

    fig.layout.coloraxis.showscale = False
    fig.layout.dragmode = False

    plot_html = plotly.io.to_html(fig, 
        include_plotlyjs=False, 
        full_html=True, 
        config={'displayModeBar': False})

    plot_html = format_html(plot_html, total_confirmed)

    with open('index.html', 'w') as fh:
        fh.write(plot_html)

    return total_confirmed # Used to check if there's changes in the data


if __name__ == '__main__':
    write_plot()



