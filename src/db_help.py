import sys
import sqlite3
from contextlib import closing

import helpers


def get_apps(database: str) -> list[helpers.App]:
  ret = []

  try:
    with closing(sqlite3.connect(database)) as conn:
      res = conn.execute("SELECT * FROM Apps")
      ret = [helpers.App(*d) for d in res.fetchall()]
  except sqlite3.OperationalError as exc:
    if "no such table: Apps" in str(exc):
      setup(database)
  finally:
    if len(ret) == 0:
      print("you have no apps, maybe add some first?")
    return ret


def update_version(
  database: str, version: str, name: str, app_id: str
) -> None:
  with closing(sqlite3.connect(database)) as conn:
    conn.execute("""
      UPDATE Apps
      SET version = ?, name = ?
      WHERE appID = ?
    """, (version, name, app_id))
    conn.commit()


def add_app(database: str, link: str) -> None:
  app_id = helpers.find_app_id(link)

  try:
    with closing(sqlite3.connect(database)) as conn:
      conn.execute("""
        INSERT INTO Apps (appID)
        VALUES (?)
      """, (app_id,))
      conn.commit()
  except sqlite3.IntegrityError:
    sys.exit("that app is already being monitored !")

  fetched_app = helpers.get(app_id)
  if fetched_app is None:
    remove_app(database, link, False)
    sys.exit("couldn't fetch app, are you sure you this link is valid?")
  
  update_version(database, fetched_app.version, fetched_app.name, app_id)
  print(
    f"now monitoring '{fetched_app.name}' currently on "
    f"version {fetched_app.version} !")


def remove_app(database: str, link: str, alert=True) -> None:
  app_id = helpers.find_app_id(link)

  try:
    with closing(sqlite3.connect(database)) as conn:
      res = conn.execute("""
        SELECT COUNT(1) FROM Apps
        WHERE appID = ?
      """, (app_id,))
      assert res.fetchone()[0] > 0

      conn.execute("DELETE FROM Apps WHERE appID = ?", (app_id,))
      conn.commit()
  except AssertionError:
    sys.exit("that app is not being monitored !")

  if alert:
    print(f"removed '{app_id}' from the database !")


def setup(database: str) -> None:
  with closing(sqlite3.connect(database)) as conn:
    conn.execute("""
      CREATE TABLE Apps (
        appID TEXT NOT NULL PRIMARY KEY,
        version TEXT,
        name TEXT
      )
    """)
