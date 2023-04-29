import os
import random

import requests
from environs import Env


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

    _, filename = os.path.split(url)

    response = requests.get(image_url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)

    return filename, message


def get_server_url(access_token, group_id, version):

    url = 'https://api.vk.com/method/photos.getWallUploadServer'

    params = {
        'access_token': access_token,
        'v': version,
        'group_id': group_id,
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

    return response.json()


def save_photo_on_wall(access_token, group_id, version, photo_server):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'

    params = {
        'access_token': access_token,
        'v': version,
        'group_id': group_id,
        'photo': photo_server['photo'],
        'server': photo_server['server'],
        'hash': photo_server['hash']
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    return response.json()


def publish_photo(access_token, group_id, version, saved_photo, message):

    url = 'https://api.vk.com/method/wall.post'
    photo_owner_id = saved_photo['response'][0]['owner_id']
    photo_id = saved_photo['response'][0]['id']

    params = {
        'access_token': access_token,
        'v': version,
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': f"photo{photo_owner_id}_{photo_id}",
        'message': message,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    if response.ok:
        print(f"Комикс успешно опубликован. Номер публикации: {response.json()['response']['post_id']}")


def main():
    env = Env()
    env.read_env()

    access_token = env('VK_APPLICATION_ACCESS_TOKEN')
    group_id = env('VK_GROUP_ID')
    version = env('VK_API_VERSION')

    filename, message = get_random_xkcd_comic()
    upload_url = get_server_url(access_token, group_id, version)
    photo_server = (upload_photo(upload_url, filename))
    saved_photo = save_photo_on_wall(access_token, group_id, version, photo_server)
    publish_photo(access_token, group_id, version, saved_photo, message)
    os.remove(filename)


if __name__ == '__main__':
    main()
