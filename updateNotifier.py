from requests import get
from time import sleep


BOT_TOKEN = ""  # <-- add your bot token here. you can make a bot by messaging @BotFather
CHAT_ID = ""    # <-- add the chat id of your group or channel or whatever here
COUNTRY = "us"  # <-- two letter country code, checks for updates in the united states by default


STORE = f"https://itunes.apple.com/lookup?country={COUNTRY}&bundleId="
UPDATE_CHANNEL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=a%20new%20update%20has%20been%20released%20for%20"

bundles = {}

files = {}

req_headers = {
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",  # sometimes needed bc apple is weird
    "cache-control": "private, max-age=0, no-cache"
}


def check_version(app):
    print(f"now checking {app} for updates..")
    sleep(2)  # avoid rate limits (hopefully)

    try:
        new_ver = get(f"{STORE}{bundles[app]}", headers=req_headers).json()["results"][0]["version"]
    except IndexError:
        print(f"**ERROR**: {bundles[app]} is not a valid bundle id, so fetching the current version is impossible.")
        return

    print(f"> got new_ver {new_ver}")

    try:
        with open(files[app], "r") as oldversion:
            old_ver = oldversion.read().strip()  # .strip() is required bc theres whitespace for some reason
            print(f"< got old_ver {old_ver}")
        if new_ver != old_ver:
            send_update_message(app, new_ver, old_ver)
            print("**UPDATE**: sent message.")
            with open(files[app], "w") as replace:
                replace.write(new_ver)
                print(f"**UPDATE**: erased file and inserted new_ver: {new_ver}")
    except FileNotFoundError:
        print(f"**ERROR**: the version checking file for {app}, {files[app]}, does not exist.")
        return
    except KeyError:
        print(f"**ERROR**: the version checking file for {app} is not defined.")


def send_update_message(app, new_ver, old_ver):
    get(f"{UPDATE_CHANNEL}{app}!%0A%0Athe%20old%20version%20was%3A%20{old_ver}%0Athe%20new%20version%20is%3A%20{new_ver}")
    # don't even question it.


while 1:
    for app in bundles:
        check_version(app)
    print("rechecking in 10 minutes...\n")
    sleep(600)
