import time

import requests
from datetime import datetime
from pprint import pprint


class VkApiError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f"Ошибка API VK {self.code}"


class VkApi:
    vk_host = "https://api.vk.com/method/"

    def __init__(self, vk_id, vk_api_version="5.131",
                 vk_token="a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd"):
        self.photos = None
        self.vk_token = vk_token
        self.vk_api_version = vk_api_version

        self._set_requied_parameters()

        if vk_id.isdigit():
            self.vk_id = vk_id
        else:
            self.vk_id = self._screen_name_to_vkid(vk_id)

    def _set_requied_parameters(self):
        self.req_params = {
            "access_token": self.vk_token,
            "v": self.vk_api_version
        }

    def _screen_name_to_vkid(self, screen_name):
        method = "users.get"
        href = self.vk_host + method
        params = {"user_ids": screen_name}
        response = requests.get(url=href, params={**params, **self.req_params})
        res = response.json()
        # pprint(res)
        return str(res["response"][0]["id"])

    def _get_vk_photos_response(self, album_id, count=5 ):
        print(f"Обращение к ВК за списком фото для id {self.vk_id}, альбом {album_id}")
        vk_method = "photos.get"
        href = self.vk_host + vk_method
        params = {"owner_id": self.vk_id, "album_id": album_id, "extended": "1", "count": count,
                  "photo_sizes": "1"}
        response = requests.get(url=href, params={**params, **self.req_params})
        res = response.json()
        if response.status_code != 200 or res.get("error"): raise VkApiError(res["error"]["error_code"])

        # pprint(res)
        self.vk_response = res

    def _create_photos_list(self):
        print("Обработка ответа от VK")
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

    def get_photo_list(self, album="profile", count=5):
        while True:
            try:
                self._get_vk_photos_response(album_id=album, count=count)
            except VkApiError:
                print("Ошибка запроса к API.VK. Повтор")
                time.sleep(5)
                continue
            else:
                print("Запрос к VK успешен")
                break

        self._create_photos_list()

        return self.photos

    def get_id(self):
        return self.vk_id


if __name__ == '__main__':
    vk_test = VkApi("natalia.bardo")

    photo_list = vk_test.get_photo_list(count=10)

    pprint(photo_list)
