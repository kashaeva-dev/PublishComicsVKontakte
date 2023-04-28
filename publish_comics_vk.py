import requests
import os
from environs import Env

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


def get_wall_upload_server_vk(access_token, group_id, version):

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


def save_wall_photo_vk(upload_url, filename):

    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    access_token = env('VK_TEST_5_TASK_ACCESS_TOKEN')
    group_id = env('VK_PUBLISH_XKCD_COMICS_GROUP_ID')
    version = env('VK_API_VERSION')
    print(get_wall_upload_server_vk(access_token, group_id, version))
