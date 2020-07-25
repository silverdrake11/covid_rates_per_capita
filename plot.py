import plotly
import plotly.graph_objects as go
from bs4 import BeautifulSoup

from chart import get_ascii_chart
from frames import SCALING_FACTOR, ROUNDING_FACTOR


def format_rate_per_capita(value, data_column):
    if data_column == 'confirmed':
        cases = 'cases'
    elif data_column == 'recent':
        cases = 'recently'
    else:
        cases = 'deaths'
    population_size = int(SCALING_FACTOR[data_column] / 1000)
    rounding_factor = ROUNDING_FACTOR[data_column]
    if rounding_factor:
        value = round(value, rounding_factor)
    else:
        value = round(value)
    return "{} {} per {}k".format(value, cases, population_size)


def df_get_hover_text(row, colors_column, data_column):
    ascii_chart =''
    ascii_chart = get_ascii_chart(row['codes'], data_column).replace('\n','<br>').replace(' ','&nbsp;')
    per_capita_text = format_rate_per_capita(row[colors_column], data_column)
    population_text = "{}m".format(round(row['pop'] / 1e6, 1))
    text = ('<b>{}</b><br>'
            '{} <br><br>' 
            ' Confirmed:  {:,} <br>'
            ' Deaths:     {:,} <br>' 
            ' Population: {} <br>'
            '{}').format(row['states'], per_capita_text, row['confirmed'], 
            row['deaths'], population_text, ascii_chart) 
    return text


def get_plot_html(df, colors_column, data_column):
    
    df['text'] = df.apply(df_get_hover_text, args=(colors_column,data_column), axis=1)

    choropleth = go.Choropleth(
        locations=df['codes'],
        z=df[colors_column],
        locationmode = 'USA-states',
        colorscale = 'sunsetdark',
        hovertemplate = '%{text}<extra></extra>',
        showscale=False,
        text=df['text'],
        )
    fig = go.Figure(data=choropleth)

    fig.layout.geo = {
        'scope':'usa',
        'showlakes':False,
    }
    fig.layout.dragmode = False
    fig.layout.autosize = True
    fig.layout.margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0,
    )
    fig.layout.hoverlabel = {'font_family':"Courier New, Monospace"}

    plot_html = plotly.io.to_html(fig, 
        include_plotlyjs=False, 
        full_html=False, 
        config={'displayModeBar': False})

    # Remove problematic div tag
    soup = BeautifulSoup(plot_html, 'html.parser')
    soup.div.unwrap()
    plot_html = str(soup)

    return plot_html