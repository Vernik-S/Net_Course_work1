from pprint import pprint
from datetime import datetime
from collections import Counter

import requests
import json


class Backuper:
    vk_host = "https://api.vk.com/method/"
    ya_host = "https://cloud-api.yandex.net:443"

    def __init__(self, vk_id, ya_token, count=5, album_id="profile", vk_api_version="5.131",
                 vk_token="a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd"):
        self.photos = None
        self.ya_token = ya_token
        self.vk_token = vk_token
        self.vk_api_version = vk_api_version
        self.count = count
        self.album_id = album_id

        self._set_requied_parameters()

        if vk_id.isdigit():
            self.vk_id = vk_id
        else:
            self.vk_id = self._screen_name_to_vkid(vk_id)

    def _get_vk_photos_response(self):
        vk_method = "photos.get"
        href = self.vk_host + vk_method
        params = {"owner_id": self.vk_id, "album_id": self.album_id, "extended": "1", "count": self.count,
                  "photo_sizes": "1"}
        response = requests.get(url=href, params={**params, **self.req_params})
        res = response.json()
        # pprint(res)
        self.vk_response = res

    def _create_photos_list(self):

        self.photos = []
        for item in self.vk_response["response"]["items"]:
            photo = {
                "id": item["id"],
                "size": item["sizes"][-1]["type"],
                "url": item["sizes"][-1]["url"],
                "likes": item["likes"]["count"],
                "date": datetime.utcfromtimestamp(item["date"]).strftime('%Y-%m-%d, %H-%M-%S')
            }
            self.photos.append(photo)
        # pprint(self.photos)

    def _create_filenames(self):
        likes_count = dict(Counter(photo['likes'] for photo in self.photos))
        # print(likes_count)
        for i, photo in enumerate(self.photos):
            if likes_count[photo['likes']] == 1:
                filename = str(photo['likes'])
            else:
                filename = str(photo['likes']) + "_" + str(photo['date'])
            filename += ".jpg"
            self.photos[i]["filename"] = filename
        # pprint(self.photos)

    def _copy_to_yadisk(self, dir_name=None):  # dir_name=self.vk_id почему не работает?
        if dir_name is None:
            dir_name = self.vk_id + self.album_id

        def _set_ya_headers():
            self.ya_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.ya_token}'
            }

        def _create_dir(inner_dir_name):
            method = "/v1/disk/resources"
            href = self.ya_host + method
            params = {"path": inner_dir_name, "overwrite": "true"}
            response = requests.put(url=href, headers=self.ya_headers, params=params)
            # pprint(response.json())
            return response.status_code

        _set_ya_headers()
        _create_dir(dir_name)

        method = "/v1/disk/resources/upload"
        href = self.ya_host + method
        dir_path_yadisk = dir_name + "/"
        self.response = []
        for photo in self.photos:
            file_path_yadisk = dir_path_yadisk + photo["filename"]
            params = {"url": photo["url"], "path": file_path_yadisk}  # , "fields":  "name,_embedded"}
            response = requests.post(url=href, headers=self.ya_headers, params=params)
            self.response.append({
                "file_name": photo["filename"],
                "size": photo["size"]
            })
            # pprint(response.json())
        # pprint(self.response)

    def _set_requied_parameters(self):
        self.req_params = {
            "access_token": self.vk_token,
            "v": self.vk_api_version
        }

    def _screen_name_to_vkid(self, screen_name):
        method = "users.get"
        href = self.vk_host + method
        params = {"owner_id": screen_name}
        response = requests.get(url=href, params={**params, **self.req_params})
        res = response.json()
        # pprint(res)
        return str(res["response"][0]["id"])

    def create_backup(self):

        self._get_vk_photos_response()
        self._create_photos_list()
        self._create_filenames()
        self._copy_to_yadisk()

        json_object = json.dumps(self.response)
        return json_object


if __name__ == '__main__':
    with open("yandex_token.txt") as token_file:
        ya_token = token_file.read()

    # id_begemot = "552934290"

    # id = id_begemot

    backup = Backuper("begemot_korovin", ya_token)

    pprint(backup.create_backup().json())

    # backup._get_vk_photos_response()
    # backup._create_photos_list()
    # backup._create_filenames()
    # backup._copy_to_yadisk()
