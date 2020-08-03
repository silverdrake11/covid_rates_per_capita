import os
import subprocess
import time
import traceback

from alerts import post_alerts
from helpers import STATIC_DIR, get_confirmed, get_cur_time, format_time
from pleth import write_plot
from download import download_and_write_historical


def run_git(*commands, files=[]):
    assert all([isinstance(command, str) for command in commands])
    final = ['git'] + list(commands) + list(files)
    output = subprocess.check_output(final)
    if output:
        print(output)


def get_static_filenames():
    files = []
    for filename in os.listdir(STATIC_DIR):
        if filename.startswith('.'):
            continue
        filepath = os.path.join(STATIC_DIR, filename)
        if os.path.isfile(filepath):
            files.append(filepath)
    return files


if __name__ == '__main__':

    prev_label = get_confirmed()
    while True:
        try:
            files = get_static_filenames()
            files.append('data.csv')
            run_git('checkout', files=files)
            run_git('pull')
            label = write_plot()
            if label != prev_label:
                try:
                    download_and_write_historical()
                    post_alerts()
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
