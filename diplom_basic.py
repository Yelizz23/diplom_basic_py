import json
import time
from pprint import pprint
import requests
from tqdm import tqdm


class VkUser:
    def __init__(self, token, version):
        self.params = {'access_token': token, 'v': version}

    def _get_photos(self, owner_id):
        while True:
            num = int(input('Please, enter the required quantity of photos to download: \n'))
            params = {
                'owner_id': owner_id,
                'album_id': 'profile',
                'count': num,
                'extended': 1,
                'v': 5.131
            }
            data = requests.get(VK_URL + 'photos.get', params={**self.params, **params}).json()['response']
            if num not in range(data['count'] + 1):
                pprint(f'There are {data["count"]} photos on  the required account!')
            else:
                photos_list = []
                for pictures in data['items']:
                    result = {'likes': pictures['likes']['count'],
                              'url': pictures['sizes'][- 1]['url'],
                              'size': pictures['sizes'][- 1]['type']}
                    photos_list.append(result)
                return photos_list


class YandexUser:
    def __init__(self, token: str):
        self.token = token
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                        'Authorization': f'OAuth {self.token}'}

    def _get_files(self):
        new_folder = input('Enter the required folder name on the YandexDisk: \n')
        params = {'path': new_folder}
        requests.put(YAD_URL, headers=self.headers, params=params)
        return new_folder

    def photos_upload(self, photos_list):
        folder_name = self._get_files()
        file_json = []
        for photos in tqdm(photos_list):
            time.sleep(0.33)
            file_name = f'{photos["likes"]}.jpg'
            photos_list = {'file_name': file_name, 'size': photos['size']}
            file_json.append(photos_list)
            params = {'path': f'{folder_name} | {file_name}', 'url': photos['url']}
            response_upload = requests.post(YAD_URL + '/upload', headers=self.headers, params=params)
            response_upload.raise_for_status()
            pprint(response_upload.status_code)
            if response_upload.status_code <= 400:
                pprint('Your photos have been successfully uploaded to the YandexDisk!')
            else:
                pprint(f'Error: {response_upload.status_code}')

        return json.dumps(file_json, indent=4)


if __name__ == '__main__':
    YAD_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
    VK_URL = 'https://api.vk.com/method/'

    with open('vk_token.txt', 'r') as file_obj:
        vk_token = file_obj.read().strip()
    with open('ya_token.txt', 'r') as file_obj:
        ya_token = file_obj.read().strip()

    try:
        profile_id = int(input('Please, enter profile identification number: \n'))
        vk = VkUser(vk_token, '5.131')
        yd = YandexUser(ya_token)
        files_list = vk._get_photos(profile_id)
        pprint(yd.photos_upload(files_list))
    except KeyError as error:
        pprint('You entered an invalid id number. Account does not exist!')
