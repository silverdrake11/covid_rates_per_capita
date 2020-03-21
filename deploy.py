import subprocess
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from pleth import write_plot


def get_confirmed():
    url = 'https://laughing-villani-877af6.netlify.com/'
    request = requests.get(url)
    plot_html = request.text
    soup = BeautifulSoup(plot_html, 'html.parser')
    return int(soup.body['data-total'])


prev_label = get_confirmed()
while True:
    print(subprocess.check_output(['git', 'pull']).strip())
    label = write_plot()
    if label != prev_label:
        print(subprocess.check_output(['git', 'commit', 'index.html', '-m', 'Data update']))
        print(subprocess.check_output(['git', 'push']))
    prev_label = label
    print(datetime.now())
    print()
    time.sleep(3600)