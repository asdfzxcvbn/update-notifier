import re
import sys
import json
import urllib.parse
import urllib.request
from uuid import uuid4
from typing import Optional
from contextlib import closing
from dataclasses import dataclass

import longs


@dataclass
class App:
  id: str
  version: str
  name: str


@dataclass
class Env:
  database: str
  bot_token: str
  channel_id: str | int


def get(app_id: str) -> Optional[App]:
  try:
    with closing(urllib.request.urlopen(
       "https://itunes.apple.com/lookup"
      f"?id={app_id}&limit=1&noCache={uuid4()}")
    ) as req:
      resp = json.load(req)

    return App(
      app_id,
      resp["results"][0]["version"],
      resp["results"][0]["trackName"])
  except Exception:
    return None


def find_app_id(link: str) -> str:
  search = re.search(r"\/id(\d{9,10})(?:\?|$)", link)

  if search is None:
    sys.exit("couldn't find app id, are you sure that link is valid?")

  return search.group(1)


def notify(
  name: str, old_version: str, new_version: str,
  bot_token: str, channel_id: str | int, app_id: str
) -> None:
  req = urllib.request.Request(
    f"https://api.telegram.org/bot{bot_token}/sendMessage",
    data=urllib.parse.urlencode({
      "chat_id": channel_id,
      "text": longs.update_msg % (name, old_version, new_version, app_id)
    }).encode()
  )

  closing(urllib.request.urlopen(req))
