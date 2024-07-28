import os
import sys
import argparse
from time import sleep

import db_help
import helpers

TWENTY_MINUTES = 1_200


def main(args: argparse.Namespace):
  try:
    env = helpers.Env(
      os.environ["DATABASE"],
      os.environ["BOT_TOKEN"],
      os.environ["CHANNEL_ID"])
  except KeyError:
    sys.exit(
      "please ensure DATABASE, BOT_TOKEN, and CHANNEL_ID "
      "are defined in the environment")

  if not os.path.isfile(env.database):
    db_help.setup(env.database)

  if args.cmd == "add":
    return db_help.add_app(env.database, args.link)
  elif args.cmd == "rm":
    return db_help.remove_app(env.database, args.link)

  # main logic -- start here!
  while True:
    try:
      for app in db_help.get_apps(env.database):
        print(f"checking updates for {app.name} ..")
        new_app = helpers.get(app.id)

        if new_app is None:
          print("couldn't fetch app. retrying in 20 seconds!")
          sleep(20)

          new_app = helpers.get(app.id)
          if new_app is None:
            print("still couldn't fetch app. moving on..\n")
            continue

        if new_app.version == app.version:
          print(f"no new updates, still on {app.version} !\n")
          sleep(5)  # to satisfy rate limit of 20 reqs/min
          continue

        print(f"notifying about update {app.version} -> {new_app.version} !")
        helpers.notify(
          app.name, app.version, new_app.version,
          env.bot_token, env.channel_id, app.id)
        db_help.update_version(
          env.database, new_app.version, new_app.name, app.id)
        print("notified!\n")
        sleep(5)

        print("done checking all apps, rechecking in 20 minutes !")
        sleep(TWENTY_MINUTES)
    except KeyboardInterrupt:
      print(" -- bye!")
      sys.exit(0)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="an update notifier with no external dependencies!")
  subparsers = parser.add_subparsers(dest="cmd")
  subparsers.required = True

  subparsers.add_parser("start", help="start monitoring")

  add_app_parser = subparsers.add_parser("add", help="monitor a new app")
  add_app_parser.add_argument(
    "-l", "--link", required=True,
    help="the link of the app to monitor")

  rm_app_parser = subparsers.add_parser("rm", help="stop monitoring an app")
  rm_app_parser.add_argument(
    "-l", "--link", required=True,
    help="the link of the app to stop monitoring")

  main(parser.parse_args())
