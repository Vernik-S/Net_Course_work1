import requests
from datetime import datetime
from pprint import pprint
from collections import Counter

class YndApiError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"Yandex API Error {self.code}"

class YndApi:
    ya_host = "https://cloud-api.yandex.net:443"

    def __init__(self, ya_token):


        self.ya_token = ya_token
        self._set_ya_headers()



    def _set_ya_headers(self):
        self.ya_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.ya_token}'
        }

    def copy_to_yadisk(self, dir_name, photos):
        def _create_filenames():
            print("Генерация имен файлов")
            likes_count = dict(Counter(photo['likes'] for photo in self.photos))
            # print(likes_count)
            for i, photo in enumerate(self.photos):
                filename = str(photo['likes'])
                if likes_count[photo['likes']] > 1:
                    filename += "_" + str(photo['date'])
                filename += ".jpg"
                self.photos[i]["filename"] = filename

        def _create_dir(inner_dir_name):
            print(f"Создание директории {inner_dir_name}")
            method = "/v1/disk/resources"
            href = self.ya_host + method
            params = {"path": inner_dir_name, "overwrite": "true"}
            response = requests.put(url=href, headers=self.ya_headers, params=params)
            if response.status_code not in  (202, 409): raise YndApiError(response.status_code)
            # pprint(response.json())
            return response.status_code

        def _get_disk_name():
            method = "/v1/disk/"
            href = self.ya_host + method
            params = {"fields": "user"}
            response = requests.get(url=href, headers=self.ya_headers, params=params)
            if response.status_code != 200: raise YndApiError(response.status_code)
            res = response.json()
            return res["user"]["login"]


        self.photos = photos
        _create_dir(dir_name)
        _create_filenames()

        method = "/v1/disk/resources/upload"
        href = self.ya_host + method
        dir_path_yadisk = dir_name + "/"
        self.response = []
        print(f"Загрузка {len(self.photos)} фото на Яндекс.Диск {_get_disk_name()}:")

        for i, photo in enumerate(self.photos):
            file_path_yadisk = dir_path_yadisk + photo["filename"]
            params = {"url": photo["url"], "path": file_path_yadisk}  # , "fields":  "name,_embedded"}
            response = requests.post(url=href, headers=self.ya_headers, params=params)
            if response.status_code == 202:
                self.response.append({
                    "file_name": photo["filename"],
                    "size": photo["size"]
                })
                msg = "Загружен"
            else:
                msg = "Не загружен"
            print(msg, end="")
            print(f" файл {file_path_yadisk}. Выполнено {(i + 1) / len(self.photos) * 100:.2f}%")
            # pprint(response.json())
        # pprint(self.response

    def get_response(self):
        return self.response
