# flickr-to-yadisk

Migrate all photos from flickr to Yandex.Disk without downloading them on a local machine. The speed of export is tunable and can easy reach 100 photos per minute, exercise caution in order not to exceed API calls quota.

## Motivation

I used Flickr as a close-to-unlimited storage for my vacation photos. In the end of 2018 they announced that they will no longer give 1 TB on their service, so the payment for pro-subscription should be done in order not to lose all of the data. In February, 2019 all photos exceeding a small quota will be deleted.

So I didn't want to spend money on yet another service subscription and decided to migrate photos to some other storage service before they get deleted at Flickr. Luckily I had enough room on Yandex.Disk, so it was decided to be used as a destination. However I tried to keep the code as extendable as possible, so in case you want to migrate to other service, the only thing you need is just to add a new API wrapper in `clients` package.
