import os
import random
from dataclasses import dataclass

import requests
from environs import Env


@dataclass
class Credentials:
    access_token: str
    group_id: str
    version: str


class VkApiError(Exception):

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f'VK API error: {self.error_code}: {self.error_message}')


def check_for_vk_api_errors(response):
    if 'error' in response:
        raise VkApiError(response['error']['error_code'], response['error']['error_msg'])


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

    return image_url, filename, message


def save_image(image_url, filename):

    response = requests.get(image_url)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def get_upload_url(vk: Credentials):

    url = 'https://api.vk.com/method/photos.getWallUploadServer'

    params = {
        'access_token': vk.access_token,
        'v': vk.version,
        'group_id': vk.group_id,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_settings = response.json()
    check_for_vk_api_errors(upload_settings)

    upload_url = upload_settings['response']['upload_url']

    return upload_url


def upload_photo(upload_url, filename):

    with open(filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)

    response.raise_for_status()

    uploaded_photo = response.json()
    check_for_vk_api_errors(uploaded_photo)

    return uploaded_photo['photo'], uploaded_photo['server'], uploaded_photo['hash']


def save_photo_on_wall(vk: Credentials, photo, server, hash_):

    url = 'https://api.vk.com/method/photos.saveWallPhoto'

    params = {
        'access_token': vk.access_token,
        'v': vk.version,
        'group_id': vk.group_id,
        'photo': photo,
        'server': server,
        'hash': hash_,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    saved_photo = response.json()
    check_for_vk_api_errors(saved_photo)

    owner_id = saved_photo['response'][0]['owner_id']
    photo_id = saved_photo['response'][0]['id']

    return owner_id, photo_id


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
    response.raise_for_status()
    post = response.json()
    check_for_vk_api_errors(post)

    return post['response']['post_id']


def main():
    env = Env()
    env.read_env()
    vk = Credentials(
        access_token=env('VK_APPLICATION_ACCESS_TOKEN'),
        group_id=env('VK_GROUP_ID'),
        version=env('VK_API_VERSION'),
    )

    image_url, filename, message = get_random_xkcd_comic()

    try:
        save_image(image_url, filename)
        upload_url = get_upload_url(vk)
        photo, server, hash_ = upload_photo(upload_url, filename)
        photo_owner_id, photo_id = save_photo_on_wall(vk, photo, server, hash_)
        post_id = publish_photo(vk, photo_owner_id, photo_id, message)
        if post_id:
            print(f'Комикс успешно опубликован. Номер публикации: {post_id}!')
    except VkApiError as error:
        print(f"Ошибка VK API (код ошибки - {error.error_code}): {error.error_message}")
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()
