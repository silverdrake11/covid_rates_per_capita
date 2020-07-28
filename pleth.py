import os

import jinja2

import data
from chart import get_last_n
from helpers import STATIC_DIR, get_cur_time, format_time
from frames import get_most_recent_df
from plot import get_plot_html


TITLE = "US Covid-19 Rates Per Capita"
HTML_TITLE = TITLE + " (Coronavirus)"
DESCRIPTION = "A map tracking the United States confirmed COVID-19 cases. The darker colors correspond to a greater rate per capita measurement."
HOMEPAGE = 'https://us-covid19-per-capita.net'
TEMPLATE_FILENAME = 'templates/template.html'
MILITARY_AND_OTHER_CASES = 0 #25963 TODO   
MILITARY_AND_OTHER_DEATHS = 0 #1047 TODO


def write_index_page(df, total_confirmed, total_deaths, time_updated):

    plot_html = get_plot_html(df, 'rate', 'confirmed')

    text = open(TEMPLATE_FILENAME).read()
    t = jinja2.Template(text)
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=format_time(time_updated),
            title=TITLE,
            html_title=HTML_TITLE,
            description=DESCRIPTION,
            link=HOMEPAGE,
            utc=time_updated.isoformat())

    with open(os.path.join(STATIC_DIR, 'index.html'), 'w') as fh:
        fh.write(rendered)


def load_jinja(template_name):
    # We need to do this b/c it refers to the other template
    template_loader = jinja2.FileSystemLoader(searchpath='./templates')
    template_env = jinja2.Environment(loader=template_loader)
    return template_env.get_template(template_name)


def write_recent_page(df, total_confirmed, total_deaths, time_updated):

    page_filename = os.path.join(STATIC_DIR, 'recent.html')
    description = 'A map of USA confirmed Coronavirus cases in the past week (per state population).'

    plot_html = get_plot_html(df, 'rrate', 'recent')

    t = load_jinja('recent_template.html')
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=format_time(time_updated),
            title=TITLE.replace('Rates', 'Recent Cases'),
            html_title=HTML_TITLE.replace('Rates', 'Recent Cases'),
            description=description,
            link=HOMEPAGE + '/' + page_filename,
            utc=time_updated.isoformat())

    with open(page_filename, 'w') as fh:
        fh.write(rendered)


def write_recent_deaths_page(df, total_confirmed, total_deaths, time_updated):

    page_filename = os.path.join(STATIC_DIR, 'recent_deaths.html')
    description = 'A map of USA confirmed Coronavirus deaths in the past week (per state population).'

    plot_html = get_plot_html(df, 'rdrate', 'recentd')

    t = load_jinja('recent_deaths_template.html')
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=format_time(time_updated),
            title=TITLE.replace('Rates', 'Recent Deaths'),
            html_title=HTML_TITLE.replace('Rates', 'Recent Deaths'),
            description=description,
            link=HOMEPAGE + '/' + page_filename,
            utc=time_updated.isoformat())

    with open(page_filename, 'w') as fh:
        fh.write(rendered)


def write_deaths_page(df, total_confirmed, total_deaths,  time_updated):

    page_filename = os.path.join(STATIC_DIR, 'deaths.html')
    description = 'A map of USA death rates per state population from the Coronavirus (in this case per 100,000 people). Tap or hover to display the numbers.'

    plot_html = get_plot_html(df, 'drate', 'deaths')

    t = load_jinja('deaths_template.html')
    rendered = t.render(plot=plot_html, 
            confirmed=total_confirmed,
            deaths=total_deaths,
            updated=format_time(time_updated),
            title=TITLE.replace('Rates', 'Deaths'),
            html_title=HTML_TITLE.replace('Rates', 'Deaths'),
            description=description,
            link=HOMEPAGE + '/' + page_filename,
            utc=time_updated.isoformat())

    with open(page_filename, 'w') as fh:
        fh.write(rendered)


def write_plot():

    # Init
    get_last_n.cache_clear()

    df = get_most_recent_df()

    # Write csv
    csv_df = df[['codes','confirmed','deaths','recovered']]
    csv_df = csv_df.sort_values(['codes'])
    csv_df.to_csv('data.csv',index=False)

    total_confirmed = df.confirmed.sum() + MILITARY_AND_OTHER_CASES
    total_deaths = df.deaths.sum() + MILITARY_AND_OTHER_DEATHS
    time_updated = get_cur_time()

    write_index_page(df, total_confirmed, total_deaths, time_updated)
    write_deaths_page(df, total_confirmed, total_deaths, time_updated)
    write_recent_page(df, total_confirmed, total_deaths, time_updated)
    write_recent_deaths_page(df, total_confirmed, total_deaths, time_updated)

    return total_confirmed # Used to check if there's changes in the data


if __name__ == '__main__':
    write_plot()
