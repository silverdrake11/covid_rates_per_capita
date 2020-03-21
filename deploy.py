import subprocess
import time

import requests
from bs4 import BeautifulSoup

from pleth import write_plot


def get_confirmed():
    url = ''
    #requests.get(url, headers=headers)
    #plot_html = requests.text
    plot_html = open('index.html').read()
    soup = BeautifulSoup(plot_html, 'html.parser')
    return soup.body['data-total']


prev_label = get_confirmed()
while True:
    print(subprocess.check_output(['git', 'pull']).strip())
    label = write_plot()
    if label != prev_label:
        print(subprocess.check_output(['git', 'commit', 'index.html']))
        print(subprocess.check_output(['git', 'push']))
    prev_label = label
    time.sleep(30)