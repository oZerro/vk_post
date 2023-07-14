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


def get_upload_url(token, group_id):
    vk_api_url = 'https://api.vk.com/method/'
    params = {
        'access_token': token,
        'v': 5.131,
        'group_id': group_id
    }
    method = 'photos.getWallUploadServer'
    response = requests.get(f'{vk_api_url}{method}', params=params)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_owner_id_and_photo_id(token, group_id, server, vk_hash, photo):
    vk_api_url = 'https://api.vk.com/method/'
    method = 'photos.saveWallPhoto'
    params = {
        'access_token': token,
        'v': 5.131,
        'group_id': group_id,
        'server': server,
        'hash': vk_hash,
        'photo': photo
    }
    response = requests.post(f'{vk_api_url}{method}', data=params)
    response.raise_for_status()
    response = response.json()
    owner_id = response['response'][0]['owner_id']
    photo_id = response['response'][0]['id']

    return owner_id, photo_id


def wall_post(token, message, owner_id, photo_id, group_id):
    vk_api_url = 'https://api.vk.com/method/'
    method = 'wall.post'

    params = {
        'access_token': token,
        'v': 5.131,
        'owner_id': -int(group_id),
        'from_group': 1,
        'message': message,
        'attachments': f'photo{owner_id}_{photo_id}'
    }

    response = requests.post(f'{vk_api_url}{method}', data=params)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    group_id = os.environ['GROUP_ID']
    token = os.environ['VK_TOKEN']

    url = 'https://xkcd.com/info.0.json'
    response = get_response(url).json()
    number = response['num']
    message = response['alt']
    random_num = random.randint(1, number)
    random_comic_url = f'https://xkcd.com/{random_num}/info.0.json'

    response = get_response(random_comic_url).json()

    Path("images").mkdir(parents=True, exist_ok=True)
    file_format = get_file_extension(response['img'])
    save_img(response['img'], {}, f"comic_{random_num}{file_format}")

    with open(f'images/komiks_{random_num}{file_format}', 'rb') as file:
        url = get_upload_url(token, group_id)
        files = {
            'photo': file, 
        }
        response = requests.post(url, files=files)

    response.raise_for_status()
    response = response.json()
    server = response['server']
    vk_hash = response['hash']
    photo = response['photo']

    owner_id, photo_id = get_owner_id_and_photo_id(token, group_id, server, vk_hash, photo)

    wall_post(token, message, owner_id, photo_id, group_id)

    os.remove(f'images/komiks_{random_num}.png')









