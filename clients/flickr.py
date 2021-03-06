import sys
import time

import oauth2
import requests


def read_api_keys(fname, classname, first_key_name, second_key_name):
    with open(fname, 'r') as f:
        first_key = f.readline().strip()
        second_key = f.readline().strip()

    # could've been done much better, but no
    return type(
        classname,
        (),
        {
            first_key_name: first_key,
            second_key_name: second_key,
        }
    )


API_KEYS = read_api_keys('.apikeys', 'APIKeys', 'key', 'secret')
TOKEN_KEYS = read_api_keys('.token', 'TokenKeys', 'token', 'secret')

BASE_FLICKR_API_URL = 'https://api.flickr.com/services/rest'
FLICKR_GET_PHOTOSETS_METHOD = 'flickr.photosets.getList'
FLICKR_GET_PHOTOSET_METHOD = 'flickr.photosets.getPhotos'
FLICKR_GET_PHOTO_SIZES_METHOD = 'flickr.photos.getSizes'


class FlickrAPIRequestBase:

    def __init__(self, params_override=None):
        params_override = params_override or {}

        self._consumer = oauth2.Consumer(key=API_KEYS.key, secret=API_KEYS.secret)
        self._token = oauth2.Token(TOKEN_KEYS.token, TOKEN_KEYS.secret)
        self._url = BASE_FLICKR_API_URL

        defaults = {
            'format': 'json',
            'nojsoncallback': 1,
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': oauth2.generate_nonce(),
            'signature_method': 'HMAC-SHA1',
            'oauth_token': self._token.key,
            'oauth_consumer_key': self._consumer.key,
        }
        defaults.update(params_override)

        self._parameters = defaults

    def perform(self):
        req = oauth2.Request(
            method='GET',
            url=self._url,
            parameters=self._parameters
        )

        req['oauth_signature'] = oauth2.SignatureMethod_HMAC_SHA1().sign(
            req,
            self._consumer,
            self._token
        )

        response_json = None
        retry_timeout = 1.33
        for _ in range(5):
            try:
                response = requests.get(req.to_url(), timeout=10)
                response.raise_for_status()
                response_json = response.json()
            except Exception:
                print('retrying request...', file=sys.stderr)
                time.sleep(retry_timeout)
                retry_timeout *= 1.25
                continue
            else:
                break

        if response_json is None:
            print('exception happened while doing a request {}'.format(self._parameters['method']), sys.stderr)

        return response_json


class FlickrAPIGetPhotosetsRequest(FlickrAPIRequestBase):

    def __init__(self, user_id):
        super().__init__({
            'method': FLICKR_GET_PHOTOSETS_METHOD,
            'user_id': user_id,
        })


class FlickrAPIGetPhotosetRequest(FlickrAPIRequestBase):

    def __init__(self, user_id, photoset_id, page):
        super().__init__({
            'method': FLICKR_GET_PHOTOSET_METHOD,
            'user_id': user_id,
            'photoset_id': photoset_id,
            'page': str(page),
        })


class FlickrAPIGetPhotoSizesRequest(FlickrAPIRequestBase):

    def __init__(self, photo_id):
        super().__init__({
            'method': FLICKR_GET_PHOTO_SIZES_METHOD,
            'photo_id': photo_id,
        })


class FlickrClient:

    class FlickrAlbumDescription:

        def __init__(self, name, album_id):
            self.name = name
            self.album_id = album_id

    def __init__(self, user_id):
        self._user_id = user_id

    def get_albums_data(self, exclude_names=None):
        exclude_names = exclude_names or []

        request = FlickrAPIGetPhotosetsRequest(user_id=self._user_id)
        result = request.perform()
        if result is None:
            return None

        albums = []
        for descr_json in result['photosets']['photoset']:
            if descr_json['title']['_content'] in exclude_names:
                continue

            albums.append(
                self.FlickrAlbumDescription(
                    name=descr_json['title']['_content'],
                    album_id=descr_json['id'],
                )
            )

        return albums

    def get_album_photo_ids(self, album_id):
        request = FlickrAPIGetPhotosetRequest(user_id=self._user_id, photoset_id=album_id, page=1)
        request_result = request.perform()
        photo_ids = []
        if request_result is None:
            return None

        total_pages = request_result['photoset']['pages']

        self._append_photo_ids(request_result, photo_ids)
        for page_num in range(2, total_pages + 1):
            request = FlickrAPIGetPhotosetRequest(user_id=self._user_id, photoset_id=album_id, page=page_num)
            request_result = request.perform()
            self._append_photo_ids(request_result, photo_ids)

        return photo_ids

    def get_photo_cdn_url(self, photo_id):
        request = FlickrAPIGetPhotoSizesRequest(photo_id=photo_id)
        request_result = request.perform()
        if not request_result:
            return None
        for size_info in request_result['sizes']['size']:
            if size_info['label'] == 'Original':
                return size_info['source']

        print('Photo sizes were loaded, but no Original size had been found, very strange!', file=sys.stderr)
        return None

    def _append_photo_ids(self, request_result, photo_ids):
        for photo_data in request_result['photoset']['photo']:
            photo_ids.append(photo_data['id'])
