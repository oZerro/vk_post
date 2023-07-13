import requests
import os
import random
from urllib.parse import urlparse
from os.path import split, splitext
from pathlib import Path
from dotenv import load_dotenv


def save_img(url, params=None, filename=""):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(f'images/{filename}', 'wb') as file:
        file.write(response.content)


def get_file_extension(path):
    broken_path = urlparse(path)
    filename = split(broken_path.path)[1]
    file_extension = splitext(filename)[1]
    return file_extension


def get_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def get_upload_url(url_vk_api, token, group_id):
    params = {
        'access_token': token,
        'v': 5.131,
        'group_id': group_id
    }
    method = 'photos.getWallUploadServer'
    response = requests.get(f'{url_vk_api}{method}', params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_owner_id_and_photo_id(url_vk_api, token, group_id, server, hash, photo):
    method = 'photos.saveWallPhoto'
    params = {
        'access_token': token,
        'v': 5.131,
        'group_id': group_id,
        'server': server,
        'hash': hash,
        'photo': photo
    }
    response = requests.post(f'{url_vk_api}{method}', data=params)
    response.raise_for_status()
    owner_id = response.json()['response'][0]['owner_id']
    photo_id = response.json()['response'][0]['id']

    return owner_id, photo_id


def wall_post(url_vk_api, token, message, owner_id, photo_id, group_id):
    method = 'wall.post'

    params = {
        'access_token': token,
        'v': 5.131,
        'owner_id': -group_id,
        'from_group': 1,
        'message': message,
        'attachments': f'photo{owner_id}_{photo_id}'
    }

    response = requests.post(f'{url_vk_api}{method}', data=params)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    token = os.environ['ACCES_TOKEN']
    url = 'https://xkcd.com/info.0.json'
    response = get_response(url)
    number = response.json()['num']
    message = response.json()['alt']
    random_num = random.randint(1, number)
    random_kom_url = f'https://xkcd.com/{random_num}/info.0.json'

    response = get_response(random_kom_url)

    Path("images").mkdir(parents=True, exist_ok=True)
    file_format = get_file_extension(response.json()['img'])
    save_img(response.json()['img'], {}, f"komiks_{random_num}{file_format}")

    url_vk_api = 'https://api.vk.com/method/'
    group_id = 167658562

    with open(f'images/komiks_{random_num}{file_format}', 'rb') as file:
        url = get_upload_url(url_vk_api, token, group_id)
        files = {
            'photo': file, 
        }
        response = requests.post(url, files=files)
        response.raise_for_status()

    server = response.json()['server']
    hash = response.json()['hash']
    photo = response.json()['photo']

    owner_id, photo_id = get_owner_id_and_photo_id(
        url_vk_api, token, group_id, server, hash, photo)

    wall_post(url_vk_api, token, message, owner_id, photo_id, group_id)

    os.remove(f'images/komiks_{random_num}.png')









