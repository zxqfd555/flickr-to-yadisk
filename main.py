import argparse

from clients.flickr import FlickrClient
from clients.yadisk import YaDiskClient


def recreate_album_folders(source_user_id, destination_dir):
    flickr = FlickrClient(source_user_id)
    yadisk = YaDiskClient(destination_dir)

    albums = flickr.get_albums_data(exclude_names=['Auto Upload'])
    for album in albums:
        print('Creating the respective folder for', album.name)
        yadisk.create_folder(album.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Photo migration')
    parser.add_argument('--mode', choices=['recreate-album-folders',], required=True)
    parser.add_argument('--source-user-id', required=True)
    parser.add_argument('--destination-root-dir', type=str, required=True)
    args = parser.parse_args()

    if args.mode == 'recreate-album-folders':
        recreate_album_folders(args.source_user_id, args.destination_root_dir)
