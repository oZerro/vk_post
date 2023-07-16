import requests
import os
import random
from requests import HTTPError
from urllib.parse import urlparse
from os.path import split, splitext
from pathlib import Path
from dotenv import load_dotenv


def save_img(url, params=None, photo_path=""):
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(photo_path, 'wb') as file:
        file.write(response.content)


def get_file_extension(path):
    broken_path = urlparse(path)
    filename = split(broken_path.path)[1]
    file_extension = splitext(filename)[1]
    return file_extension


def check_response_vk_api(response):
    response = response.json()
    if 'error' in response:
        raise HTTPError(f"error_msg - {response['error']['error_msg']}\n"
                        f"error_code - {response['error']['error_code']}")


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
    check_response_vk_api(response)
    return response.json()['response']['upload_url']


def save_wall_photo(token, group_id, server, vk_hash, photo):
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
    check_response_vk_api(response)
    response = response.json()
    owner_id = response['response'][0]['owner_id']
    photo_id = response['response'][0]['id']

    return owner_id, photo_id


def make_wall_post(token, message, owner_id, photo_id, group_id):
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
    check_response_vk_api(response)
    response.raise_for_status()


def save_random_comic():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()

    number = response['num']
    message = response['alt']
    random_num = random.randint(1, number)
    random_comic_url = f'https://xkcd.com/{random_num}/info.0.json'

    response = requests.get(random_comic_url)
    response.raise_for_status()
    comic_img = response.json()['img']

    Path("images").mkdir(parents=True, exist_ok=True)
    file_format = get_file_extension(comic_img)
    photo_path = f"images/comic_{random_num}{file_format}"
    save_img(comic_img, {}, photo_path)

    return photo_path, message


def upload_photo_vk_server(photo_path):
    with open(photo_path, 'rb') as file:
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

    return server, vk_hash, photo


if __name__ == '__main__':
    load_dotenv()
    group_id = os.environ['GROUP_ID']
    token = os.environ['VK_TOKEN']
    try:
        photo_path, message = save_random_comic()
        server, vk_hash, photo = upload_photo_vk_server(photo_path)
        owner_id, photo_id = save_wall_photo(token, group_id, server, vk_hash, photo)

        make_wall_post(token, message, owner_id, photo_id, group_id)
    except HTTPError as ex:
        print(ex)
    finally:
        os.remove(photo_path)









