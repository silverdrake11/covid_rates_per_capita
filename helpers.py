from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pytz import timezone


LOG_DIR = 'logs'
STATIC_DIR = 'static'


def get_cur_time():
    return datetime.now(timezone('America/Chicago'))

def format_time(datetime_obj):
    return datetime_obj.strftime("%a %b %d %-I:%M %p CST")


def get_confirmed():
    url = 'https://laughing-villani-877af6.netlify.com/'
    request = requests.get(url)
    plot_html = request.text
    soup = BeautifulSoup(plot_html, 'html.parser')
    return int(float(soup.body['data-total'])) # For example "110.0" was causing issues