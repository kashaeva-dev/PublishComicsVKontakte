import os
import random

import requests
from environs import Env
from dataclasses import dataclass

@dataclass
class Credentials:
    access_token: str
    group_id: str
    version: str


def get_random_xkcd_comic():

    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()

    comics_number = response.json()['num']
    comic_number = random.randint(1, comics_number)

    url = f'https://xkcd.com/{comic_number}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    comic = response.json()

    image_url, message = comic['img'], comic['alt']

    _, filename = os.path.split(image_url)

    response = requests.get(image_url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    return filename, message


def get_server_url(vk: Credentials):

    url = 'https://api.vk.com/method/photos.getWallUploadServer'

    params = {
        'access_token': vk.access_token,
        'v': vk.version,
        'group_id': vk.group_id,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    upload_url = response.json()['response']['upload_url']

    return upload_url


def upload_photo(upload_url, filename):

    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)

    response.raise_for_status()

    uploaded_photo = response.json()

    return (
        uploaded_photo['photo'],
        uploaded_photo['server'],
        uploaded_photo['hash']
    )


def save_photo_on_wall(vk: Credentials, photo, server, hash):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'

    params = {
        'access_token': vk.access_token,
        'v': vk.version,
        'group_id': vk.group_id,
        'photo': photo,
        'server': server,
        'hash': hash,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    saved_photo = response.json()

    return (
        saved_photo['response'][0]['owner_id'],
        saved_photo['response'][0]['id'],
    )


def publish_photo(vk: Credentials, photo_owner_id, photo_id, message):

    url = 'https://api.vk.com/method/wall.post'

    params = {
        'access_token': vk.access_token,
        'v': vk.version,
        'owner_id': f'-{vk.group_id}',
        'from_group': 1,
        'attachments': f"photo{photo_owner_id}_{photo_id}",
        'message': message,
    }

    response = requests.post(url, params=params)

    if response.ok:
        print(f"Комикс успешно опубликован. Номер публикации: {response.json()['response']['post_id']}")


def main():
    env = Env()
    env.read_env()
    vk = Credentials(
        access_token=env('VK_APPLICATION_ACCESS_TOKEN'),
        group_id=env('VK_GROUP_ID'),
        version=env('VK_API_VERSION'),
    )

    filename, message = get_random_xkcd_comic()
    upload_url = get_server_url(vk)
    photo, server, hash = (upload_photo(upload_url, filename))
    photo_owner_id, photo_id = save_photo_on_wall(vk, photo, server, hash)
    publish_photo(vk, photo_owner_id, photo_id, message)
    os.remove(filename)


if __name__ == '__main__':
    main()
