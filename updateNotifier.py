#!/usr/bin/python3
import os
import sys

if not os.path.exists(os.path.expanduser("~/.zxcvbn")) or (len(sys.argv) > 1 and sys.argv[1] == "start"):
    print("welcome to zxcvbn's update notifier!")
    print("you can get all required information by reading the README.\n")

    bot_token = input("enter your bot's token: ").strip()
    chat_id = input("enter your chat id: ").strip()
    country = input("enter your alpha-2 country code: ").lower().strip()

    if not os.path.exists(os.path.expanduser("~/.zxcvbn")):
        os.makedirs(os.path.expanduser("~/.zxcvbn"))
    with open(os.path.expanduser("~/.zxcvbn/info.py"), "w") as info:
        info.write(f"BOT_TOKEN='{bot_token}'\nCHAT_ID='{chat_id}'\nCOUNTRY='{country}'")

    print("\nall required info has been written.")
    sys.exit()

from requests import get
from time import sleep
from datetime import datetime as dt
from json import load, dump

sys.path.append(os.path.expanduser("~/.zxcvbn"))
from info import BOT_TOKEN, CHAT_ID, COUNTRY

STORE = f"https://itunes.apple.com/lookup?country={COUNTRY}&bundleId="
UPDATE_CHANNEL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text=a%20new%20update%20has%20been%20released%20for%20"

req_headers = {
    # never thought about this, but maybe bots will have correct information? lets see if apple plays nice with them.
    "User-Agent": "FreshRSS/1.11.2 (Linux; https://freshrss.org) like Googlebot",
    "cache-control": "private, max-age=0, no-cache"
}


def reload_files():
    try:
        global bundles
        global files
        with open(os.path.expanduser("~/.zxcvbn/monitor.json"), "r") as b:
            bundles = load(b)
        with open(os.path.expanduser("~/.zxcvbn/files.json"), "r") as f:
            files = load(f)
    except FileNotFoundError:
        print("you have to add an app to monitor first!")
        print("specify the app name (one word, no spaces/symbols) and bundle id to add.")
        print("usage: updates add <appname> <bundleid>")
        print("example: updates add SpotifyMusic com.spotify.client")
        sys.exit(1)


if len(sys.argv) == 1:
    pass
elif len(sys.argv) != 1 and len(sys.argv) != 4:
    print("please specify the app name (one word, no spaces/symbols) and bundle id to add.")
    print("usage: updates add <appname> <bundleid>")
    print("example: updates add SpotifyMusic com.spotify.client")
    sys.exit(1)
elif len(sys.argv) == 4 and sys.argv[1] == "add":
    try:
        current_ver = get(f"{STORE}{sys.argv[3]}", headers=req_headers).json()["results"][0]["version"].strip()
    except KeyError:
        print("invalid bundle id specified.")
        sys.exit(1)

    if not os.path.exists(os.path.expanduser("~/.zxcvbn/monitor.json")):
        with open(os.path.expanduser("~/.zxcvbn/monitor.json"), "w") as x:
            x.write("{}")
    if not os.path.exists(os.path.expanduser("~/.zxcvbn/files.json")):
        with open(os.path.expanduser("~/.zxcvbn/files.json"), "w") as x:
            x.write("{}")

    with open(os.path.expanduser("~/.zxcvbn/monitor.json"), "r") as apps:
        monitored = load(apps)
    monitored[sys.argv[2]] = sys.argv[3]
    with open(os.path.expanduser("~/.zxcvbn/monitor.json"), "w") as apps:
        dump(monitored, apps)

    with open(os.path.expanduser("~/.zxcvbn/files.json"), "r") as version_files_dict:
        version_files = load(version_files_dict)
    version_files[sys.argv[2]] = f"{os.path.expanduser('~/.zxcvbn/')}{sys.argv[2]}.txt"
    with open(os.path.expanduser("~/.zxcvbn/files.json"), "w") as version_files_dict:
        dump(version_files, version_files_dict)  # i am literally so tired rn

    with open(os.path.expanduser(f"~/.zxcvbn/{sys.argv[2]}.txt"), "w") as vfile:
        vfile.write(current_ver)

    print(f"{sys.argv[2]} is now being monitored.")
    sys.exit(1)
else:
    print("add apps usage: updates add <appname> <bundleid>")
    print("start monitoring: updates")
    sys.exit(1)


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
    reload_files()
    for app in bundles:
        check_version(app)
    print(f"current time is {dt.now().strftime('%H:%M:%S')}, rechecking in 10 minutes...\n")
    sleep(600)
