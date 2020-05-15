import subprocess
import time
import traceback

import requests
from bs4 import BeautifulSoup

from pleth import write_plot, get_cur_time, format_time
from download import download_and_write_historical


def get_confirmed():
    url = 'https://laughing-villani-877af6.netlify.com/'
    request = requests.get(url)
    plot_html = request.text
    soup = BeautifulSoup(plot_html, 'html.parser')
    return int(float(soup.body['data-total'])) # For example "110.0" was causing issues


def run_git(*commands, files=[]):
    assert all([isinstance(command, str) for command in commands])
    final = ['git'] + list(commands) + list(files)
    output = subprocess.check_output(final)
    if output:
        print(output)


prev_label = get_confirmed()
while True:
    files = ['index.html', 'data.csv', 'deaths.html', 'historical.zip']
    run_git('checkout', files=files)
    run_git('pull')
    try:
        label = write_plot()
        if label != prev_label:
            try:
                download_and_write_historical()
            except:
                traceback.print_exc()
            run_git('add', files=files)
            run_git('commit','-m', 'Data update', files=files)
            run_git('push')
        prev_label = label
    except:
        traceback.print_exc()

    print(format_time(get_cur_time()))
    print()
    time.sleep(3901)