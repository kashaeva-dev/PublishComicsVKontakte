import requests
import os

def get_image(url, filename):

    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def get_xkcd_comics(comics_number):

    url = f'https://xkcd.com/{comics_number}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    url, message = response.json()['img'], response.json()['alt']

    _, filename = os.path.split(url)

    get_image(url, filename)

    return filename, message
