# update-notifier
a telegram bot that will send updates to a channel whenever an update has been released for an app store app. apps are checked for updates every 20 minutes. **this bot will rely on files saved to your local filesystem**, however they will be stored in `~/.zxcvbn/` so they are not visible.

# installation
this script is made for macos and linux users. you can not use this on windows.

`git clone https://github.com/asdfzxcvbn/update-notifier`

`pip3 install -r update-notifier/requirements.txt`

`sudo cp update-notifier/updateNotifier.py /usr/local/bin/updates`

`sudo chmod +x /usr/local/bin/updates`

## initial setup
starting with v2, you no longer need to change any code to use the bot. you are going to have to set up your bot token, chat id, and country. run `updates start` to fill in the required info.

#### how do i get my bot token?
talk to [BotFather](https://t.me/BotFather) and make a new bot. after the bot is made, BotFather will send you the token.

#### how do i get my chat id?
refer to the following [stackoverflow answer](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id#32572159).

#### how do i get my country code?
visit [this wikipedia page](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes), find your country, and get its alpha-2 code.

## start monitoring apps
to add an app to monitor, simply run the command `updates add <appname> <bundleid>`. `<appname>` must be contain no spaces or symbols. for example, to monitor youtube:

`updates add youtube com.google.ios.youtube`

or to monitor spotify:

`updates add spotify com.spotify.client`

#### how do i get the bundle id of an app?
you can get an app's bundle id with [this website](https://offcornerdev.com/bundleid.html).

## running the bot
simply run `updates` in a terminal. the best option is to run this on a server that is always on. you can let this run in the background with tools like `screen`.

## was this useful?
if it was, i would appreciate any donation. :)
my monero address is `82m19F4yb15UQbJUrxxmzJ3fvKyjjqJM55gv8qCp2gSTgo3D8avzNJJQ6tREGVKA7VUUJE6hPKg8bKV6tTXKhDDx75p6vGj`

you may also scan this QR code.

![image](https://user-images.githubusercontent.com/109937991/227786784-28eaf0a1-9d17-4fc5-8c1c-f017fd62cfad.png)


