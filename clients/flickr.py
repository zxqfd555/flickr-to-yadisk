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

        try:
            response = requests.get(req.to_url())
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.HTTPError:
            print('Exception happened while doing a request {}'.format(self._parameters['method']), sys.stderr)
            return None

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
