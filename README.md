# update-notifier
a telegram bot that will send updates to a channel whenever an update has been released for an app store app. apps are checked for updates every 10 minutes. **this bot will rely on files saved to your local filesystem.**

## initial setup
you are going to need to update some variables. open `updateNotifier.py` and replace the first 3 variables. an example would look like this:

```python
BOT_TOKEN = "1234567890:6zzD8swuBXhY9hHaWHMFBRKsXZmR2V2R2HM"
CHAT_ID = "-1001234567890"
COUNTRY = "us"
```

#### how do i get my bot token?
talk to [BotFather](https://t.me/BotFather) and make a new bot. after the bot is made, BotFather will send you the token.

#### how do i get my chat id?
refer to the following [stackoverflow answer](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id#32572159).

#### how do i get my country code?
visit [this wikipedia page](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes), find your country, and save its alpha-2 code to `COUNTRY`.

## start monitoring apps
to begin monitoring apps, you will have to edit the `bundles` and `files` dictionaries. here's an example:

```python
bundles = {"youtube": "com.google.ios.youtube", "spotify": "com.spotify.client"}

files = {"youtube": "youtube.txt", "spotify": "spotify.txt"}
```

in this example, both youtube and spotify are being monitored for updates. to monitor new apps, add a new entry into the `bundles` dictionary with the app's name. its value will be the bundle id of the app. once you have created the new dictionary key, make a new entry in `files` with the **SAME NAME** as the entry in `bundles`. these are **case-sensitive**, so make sure even the capitalization matches. the value of the entry in `files` should be a .txt file with the name of the app you are monitoring.

you will have to create the file after you have defined it in `files`. make the file, open it in your favorite text editor, and add the current version of the app.

#### how do i get the bundle id of an app?
you can get an app's bundle id with [this website](https://offcornerdev.com/bundleid.html).

## running the bot
you'll have to install this program's dependencies. first, cd into this repo and run `python3 -m pip install -r requirements.txt`. after that, run `python3 updateNotifier.py` and leave it running. the best option is to run this on a server that is always on. you can let this run in the background with tools like `screen`.

## was this useful?
if it was, i would appreciate any donation. :)
my monero address is `82m19F4yb15UQbJUrxxmzJ3fvKyjjqJM55gv8qCp2gSTgo3D8avzNJJQ6tREGVKA7VUUJE6hPKg8bKV6tTXKhDDx75p6vGj`

you may also scan this QR code.

![image](https://user-images.githubusercontent.com/109937991/227786784-28eaf0a1-9d17-4fc5-8c1c-f017fd62cfad.png)


