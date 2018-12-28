import os
import sys
import time

import requests


API_KEY = open('.yadisk_token').read().strip()


class YaDiskClient:

    def __init__(self, destination_folder_root):
        self._root = destination_folder_root

    def create_folder(self, rel_path):
        full_path = os.path.join(self._root, rel_path)
        request_path = 'https://cloud-api.yandex.net/v1/disk/resources?path=' + full_path
        try:
            r = requests.put(
                request_path,
                headers={
                    'Authorization': 'OAuth {}'.format(API_KEY)
                }
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print('unable to perform folder creation request', file=sys.stderr)

    def save_from_url(self, url, disk_rel_path):
        full_path = os.path.join(self._root, disk_rel_path)
        request_path = (
            'https://cloud-api.yandex.net/v1/disk/resources/upload?url={}&path={}'
            .format(
                url,
                full_path
            )
        )

        success = False
        retry_timeout = 1.33
        for _ in range(5):
            try:
                r = requests.post(
                    request_path,
                    headers={
                        'Authorization': 'OAuth {}'.format(API_KEY)
                    },
                    timeout=2
                )
                r.raise_for_status()
            except Exception:
                print('retrying download assignment request...', file=sys.stderr)
                time.sleep(retry_timeout)
                retry_timeout *= 1.25
                continue
            else:
                success = True
                break

        if not success:
            print('unable to perform download assignment request')
