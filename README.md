# flickr-to-yadisk

Migrate all photos from flickr to Yandex.Disk without downloading them on a local machine. The speed of export is tunable and can easy reach 100 photos per minute, but exercise caution in order not to exceed API calls quota.

## Motivation

I used Flickr as a close-to-unlimited storage for my vacation photos. In the end of 2018 they announced that they will no longer give 1 TB on their service, so the payment for pro-subscription should be done in order not to lose all of the data. In February, 2019 all photos exceeding a small quota will be deleted.

So I didn't want to spend money on yet another service subscription and decided to migrate photos to some other storage service before they get deleted at Flickr. Luckily I had enough room on Yandex.Disk, so it was decided to be used as a destination. However I tried to keep the code as extendable as possible, so in case you want to migrate to other service, the only thing you need is just to add a new API wrapper in `clients` package.

## How to use

You'll need to have an app from Flickr App Garden - https://www.flickr.com/services/, then "Apps By You". You'll be given a Key and a Secret, which will be read from file `.apikeys` and should be separated with a newline.

Then you need to authorize yourself in Flickr OAuth, which can be done by a [tutorial](http://mkelsey.com/2011/07/03/Flickr-oAuth-Python-Example/) (you can just clone the repo and run the code). You'll get a token and a secret, which should be stored in `.token` file, again separated with a newline.

Finally, you'll need a Yandex.Disk token, which can easily be obtained by a [link](https://oauth.yandex.ru/authorize?response_type=token&client_id=b5f85a1cba424e0880a6c10af2964099). Store it in `.yadisk_token` file.

Then, you can just run the script. It has 4 supported modes, which are given through command line.

 - Get albums list. Save the list of your album names to a file. Example usage: `./main.py --mode=get-albums-list --source-user-id=<your flickr user id> --albums-list-filename=<where to save albums list>`.
 - Create folders, repeating your albums' structure at Yandex.Disk. Example usage: `./main.py --mode=recreate-album-folders --source-user-id=<your flickr user id> --destination-root-dir=<root directory for your export at yadisk>`.
 - Export one album from Flickr to Yandex.Disk. Example usage: `./main.py --mode=export-album --source-user-id=<your flickr user id> --destination-root-dir=<root directory for your export at yadisk> --album-name="<name of your album>"`.
 - Export many albums, given by a list. Example usage: `./main.py --mode=export-albums-list --source-user-id=<your flickr user id> --destination-root-dir=<root directory for your export at yadisk> --albums-list-filename=<filename of where to take the list of album names>`.

For export commands, where is also an optional parameter `rps`, denoting the number of requests per second, which the exporter is allowed to make. If it's equal to -1, then there's no limit at all. However, since there is a limit of 3600 requests per hour in Flickr API, I recommend to set rps=1 (default value) or rps=3, in case you need to export a small amount of photos and want things to run faster.
