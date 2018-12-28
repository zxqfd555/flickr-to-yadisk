import argparse
import time
import os
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock

from clients.flickr import FlickrClient
from clients.yadisk import YaDiskClient


total_processed = 0
total_processed_lock = Lock()


def recreate_album_folders(source_user_id, destination_dir):
    flickr = FlickrClient(source_user_id)
    yadisk = YaDiskClient(destination_dir)

    albums = flickr.get_albums_data(exclude_names=['Auto Upload'])
    for album in albums:
        print('Creating the respective folder for', album.name)
        yadisk.create_folder(album.name)


def export_album(source_user_id, destination_dir, album_name, rps=None):
    """
    Export a single album from Flickr to Ya.Disk.
    We assume that the respective folder is present on the Disk.

    Also note that RPS=1 should be enforced in case you have tens of thousands of
    photos, because otherwise you can hit limit of 3600 RPH.

    For smaller albums, feel free to set RPS = -1. It disables rate limiting completely
    and starts process in 8 threads.
    """
    rps = rps or 1

    flickr = FlickrClient(source_user_id)
    yadisk = YaDiskClient(destination_dir)

    albums = flickr.get_albums_data(exclude_names=['Auto Upload'])
    album_id = None
    for album in albums:
        if album.name == album_name:
            album_id = album.album_id

    if album_id:
        print('We\'ve found that album. The id is:', album_id)
    else:
        print('Album not found. Terminating.')
        return

    photo_ids = flickr.get_album_photo_ids(album_id)
    print('We\'ll export {} photos.'.format(len(photo_ids)))

    global total_processed
    total_processed = 0
    if rps > 0:
        request_timeslice = 1.0 / rps
        for photo_id in photo_ids:
            time_before = time.time()
            export_one_photo(photo_id, album_name, flickr, yadisk)
            time_spent = time.time() - time_before
            if time_spent < request_timeslice:
                time.sleep(request_timeslice - time_spent)
    else:
        pool = ThreadPool(8)
        pool.map(
            lambda photo_id: export_one_photo(photo_id, album_name, flickr, yadisk),
            photo_ids
        )


def export_one_photo(photo_id, album_name, flickr, yadisk):
    cdn_url = flickr.get_photo_cdn_url(photo_id)
    if not cdn_url:
        return

    cdn_filename = cdn_url.split('/')[-1]
    full_path = os.path.join(album_name, cdn_filename)

    yadisk.save_from_url(cdn_url, full_path)

    global total_processed
    global total_processed_lock

    total_processed_lock.acquire()
    total_processed += 1
    if total_processed % 20 == 0:
        print('{} photos had been processed.'.format(total_processed))
    total_processed_lock.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Photo migration')
    parser.add_argument(
        '--mode',
        choices=[
            'recreate-album-folders',
            'export-album',
        ],
        required=True
    )
    parser.add_argument('--source-user-id', required=True)
    parser.add_argument('--destination-root-dir', type=str, required=True)
    parser.add_argument('--album-name', type=str)
    parser.add_argument('--rps', type=int)
    args = parser.parse_args()

    if args.mode == 'recreate-album-folders':
        recreate_album_folders(args.source_user_id, args.destination_root_dir)
    elif args.mode == 'export-album':
        assert args.album_name, 'please specify album name!'
        export_album(args.source_user_id, args.destination_root_dir, args.album_name, rps=args.rps)
