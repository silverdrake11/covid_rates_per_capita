import subprocess
import time
import traceback

import requests
from bs4 import BeautifulSoup

from pleth import write_plot, get_cur_time


def get_confirmed():
    url = 'https://laughing-villani-877af6.netlify.com/'
    request = requests.get(url)
    plot_html = request.text
    soup = BeautifulSoup(plot_html, 'html.parser')
    return int(soup.body['data-total'])


prev_label = get_confirmed()
while True:
    subprocess.check_output(['git', 'checkout', 'index.html'])
    subprocess.check_output(['git', 'pull'])
    try:
        label = write_plot()
        if label != prev_label:
            print(subprocess.check_output(['git', 'commit', 'index.html', '-m', 'Data update']))
            print(subprocess.check_output(['git', 'push']))
        prev_label = label
    except:
        traceback.print_exc()

    print(get_cur_time())
    print()
    time.sleep(3600)