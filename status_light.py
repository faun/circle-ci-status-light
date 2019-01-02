#!/usr/bin/env python
import sys
import signal
import time
import random
import yaml
from download_worker import DownloadWorker
import colorsys
import blinkt

config = yaml.load(open('config.yml'))
api_token = str(config['BUILDKITE_API_KEY'])

blinkt.set_clear_on_exit()


def msleep(x):
    time.sleep(x / 1000.0)


def random_pixels():
    return [random_color() for _ in range(8)]


def random_color():
    return [random.randint(0, 128) for _ in range(3)]


def crazy_colors():
    set_colors(random_pixels())


def set_colors(colors):
    print("Setting colors... {}".format(colors))
    for i in range(len(colors)):
        r, g, b = tuple(colors[i])
        print("Setting {} to {}, {}, {}".format(i, r, b, g))
        blinkt.set_pixel(i, r, g, b, 0.1)

    blinkt.show()


def red():
    return (42, 0, 0)


def green():
    return (0, 42, 0)


def blue():
    return (0, 0, 42)


def yellow():
    return (255, 89, 0)


def white():
    return (42, 42, 42)


def black():
    return (0, 0, 0)


def brown():
    return (102, 30, 0)


def purple():
    return (128, 0, 255)


def pink():
    return (192, 0, 128)


def orange():
    return (255, 89, 61)


def grey():
    return (18, 18, 18)


def state_to_color(color):
    return {
        'passed': green(),
        'canceled': yellow(),
        'failed': red(),
        'running': white(),
        'scheduled': pink(),
        'blocked': purple(),
        'canceling': orange(),
        'error': purple(),
        'skipped': brown(),
        'not_run': black(),
        'finished': grey(),
    }[color]


def translate_build_state_colors(build_states):
    return [state_to_color(color) for color in build_states]


def reset_colors():
    colors = [[0 for _ in range(3)] for _ in range(8)]
    set_colors(colors)
    return True


def main(Loading):
    if Loading:
        reset_colors()
    urls = config['urls']
    worker = DownloadWorker(api_token)

    colors = []
    for url in urls:
        print('Queueing {}'.format(url))
        if Loading:
            crazy_colors()
        states = worker.fetch_first_eight_build_states(url)
        colors = translate_build_state_colors(states[::-1]) + colors
        print('Done')
    set_colors(colors)
    msleep(10000)

    main(False)

def signal_handler(signal, frame):
    exit_gracefully()

def exit_gracefully(self):
    reset_colors()
    sys.exit(0)

if __name__ == "__main__":
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        main(True)

    except KeyboardInterrupt:
        exit_gracefully()

    except Exception as e:
        print("Quitting... {}".format(e))
        reset_colors()
        sys.exit(1)

    finally:
        exit_gracefully()
