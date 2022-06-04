from vk_api import VkApi
from yandex_api import YndApi
import json


class Backuper:

    def __init__(self, vk_id, ya_token, vk_api_version="5.131",
                 vk_token="a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd",
                 ):
        self.response = None
        self.photos = None
        self.vk_api = VkApi(vk_id, vk_api_version, vk_token)
        self.vk_id = self.vk_api.get_id()
        self.ynd_api = YndApi(ya_token)

    def create_backup(self, count=5, album_id="profile", dir_name=None):
        if dir_name is None:
            dir_name = self.vk_id + album_id

        self.photos = self.vk_api.get_photo_list(album=album_id, count=count)

        self.ynd_api.copy_to_yadisk(dir_name=dir_name, photos=self.photos)
        self.response = self.ynd_api.get_response()
        print("Завершено.")

        json_object = json.dumps(self.response)
        return json_object

    def create_report_file(self, filename="report.txt"):
        with open(filename, "w") as report_file:
            json.dump(self.response, report_file, indent=2)
