from requests import get
from time import sleep
from datetime import datetime as dt

# don't edit anything above this line if you just want to use the bot.

BOT_TOKEN = ""  # <-- add your bot token here. you can make a bot by messaging @BotFather
CHAT_ID = ""    # <-- add the chat id of your group or channel or whatever here
COUNTRY = "us"  # <-- two letter country code, checks for updates in the united states by default

bundles = {}

files = {}

# don't edit anything below this line if you just want to use the bot.

STORE = f"https://itunes.apple.com/lookup?country={COUNTRY}&bundleId="
UPDATE_CHANNEL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=a%20new%20update%20has%20been%20released%20for%20"

req_headers = {
    # never thought about this, but maybe bots will have correct information? lets see if apple plays nice with them.
    "User-Agent": "FreshRSS/1.11.2 (Linux; https://freshrss.org) like Googlebot",
    "cache-control": "private, max-age=0, no-cache"
}


def is_newer_version(new_version, old_version):
    new_components = list(map(int, new_version.split('.')))
    old_components = list(map(int, old_version.split('.')))
    for i in range(3):
        if new_components[i] > old_components[i]:
            return True
        if new_components[i] < old_components[i]:
            return False
    return False


def check_version(app):
    print(f"now checking {app} for updates..")
    sleep(2)  # avoid rate limits (hopefully)

    try:
        request = get(f"{STORE}{bundles[app]}", headers=req_headers).json()["results"][0]
        new_ver = request["version"]
    except IndexError:
        print(f"**ERROR**: {bundles[app]} is not a valid bundle id, so fetching the current version is impossible.")
        return

    print(f"> got new_ver {new_ver}")

    try:
        with open(files[app], "r") as oldversion:
            old_ver = oldversion.read().strip()  # .strip() is required bc theres whitespace for some reason
            print(f"< got old_ver {old_ver}")

        if new_ver != old_ver:
            if is_newer_version(new_ver, old_ver):
                send_update_message(app, new_ver, old_ver, request["trackViewUrl"].replace("?uo=4", ""))
                print("**UPDATE**: sent message.")
                with open(files[app], "w") as replace:
                    replace.write(new_ver)
                    print(f"**UPDATE**: erased file and inserted new_ver: {new_ver}")
            else:
                print("**API**: itunes api returned an older version after returning a newer version. skipping.")
    except FileNotFoundError:
        print(f"**ERROR**: the version checking file for {app}, {files[app]}, does not exist.")
        return
    except KeyError:
        print(f"**ERROR**: the version checking file for {app} is not defined.")


def send_update_message(app, new_ver, old_ver, link):
    get(f"{UPDATE_CHANNEL}{app}!%0A%0Athe%20old%20version%20was%3A%20{old_ver}%0Athe%20new%20version%20is%3A%20{new_ver}%0A%0Acheck%20it%20out%20here%3A%20{link}")
    # don't even question it.


while 1:
    for app in bundles:
        check_version(app)
    print(f"current time is {dt.now().strftime('%H:%M:%S')}, rechecking in 10 minutes...\n")
    sleep(600)
