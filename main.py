from pprint import pprint
import os
from backuper import Backuper

try:
    from yandex_token import yandex_token_from_file
except:
    pass

if __name__ == '__main__':
    # print(os.environ)
    try:
        ya_token = os.environ["super_secret"]
        print("Token from environment")
    except:
        ya_token = yandex_token_from_file
        print("Token from file")

    backup = Backuper("begemot_korovin", ya_token)  # ya_token

    # backup = Backuper("natalia.bardo", yandex_token)

    pprint(backup.create_backup(count=10))

    # backup.create_report_file()
