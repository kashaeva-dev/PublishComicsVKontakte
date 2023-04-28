import os

import requests
from environs import Env
import random


def get_image(url, filename):

    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def get_total_xkcd_comics_number():

    url = 'https://xkcd.com/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    return response.json()['num']


def get_xkcd_comics(comics_number):

    url = f'https://xkcd.com/{comics_number}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    url, message = response.json()['img'], response.json()['alt']

    _, filename = os.path.split(url)

    get_image(url, filename)

    return filename, message


def get_vk_upload_wall_url(access_token, group_id, version):

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


def upload_photo_to_vk_wall_server(upload_url, filename):

    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

    return response.json()


def save_server_photo_on_wall_vk(access_token, group_id, version, photo_server):

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


def publish_comics_on_wall_vk(access_token, group_id, version, saved_photo, message):

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

    access_token = env('VK_TEST_5_TASK_ACCESS_TOKEN')
    group_id = env('VK_PUBLISH_XKCD_COMICS_GROUP_ID')
    version = env('VK_API_VERSION')
    comics_number = random.randint(1, get_total_xkcd_comics_number())
    filename, message = get_xkcd_comics(comics_number)

    upload_url = get_vk_upload_wall_url(access_token, group_id, version)
    photo_server = (upload_photo_to_vk_wall_server(upload_url, filename))
    saved_photo = save_server_photo_on_wall_vk(access_token, group_id, version, photo_server)
    publish_comics_on_wall_vk(access_token, group_id, version, saved_photo, message)
    os.remove(filename)

if __name__ == '__main__':
    main()
