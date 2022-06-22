import contextlib
import logging
import os
import sqlite3
from urllib.request import pathname2url

from flask import g


def run_query(query, args=()):
    with contextlib.closing(__get_db__()) as conn:  # auto-closes
        with conn:  # auto-commits
            with contextlib.closing(conn.cursor()) as cursor:  # auto-closes
                cursor.execute("PRAGMA foreign_keys=1;")  # Foreign keys must be enabled every time the connection is opened

            with contextlib.closing(conn.cursor()) as cursor:  # auto-closes
                try:
                    result = cursor.execute(query, args)
                    return [dict(ix) for ix in result.fetchall()]
                except sqlite3.IntegrityError:
                    return []


def __get_db__(mode="rw"):
    db_uri = 'file:{}?mode={}'.format(pathname2url(f"/home/instance/{os.environ['SVC_TYPE']}.sqlite"), mode)
    db = sqlite3.connect(
                db_uri,
                uri=True,
                detect_types=sqlite3.PARSE_DECLTYPES,
                isolation_level=None
            )
    db.row_factory = sqlite3.Row

    return db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    try:
        __get_db__()  # Opening the DB as RW. This raises an exception if the file doesn't exist
    except sqlite3.OperationalError:
        __init_db__()


def __init_db__():
    logging.info("Initializing database...")
    db = __get_db__("rwc")

    with open(f"{os.getcwd()}/schema.sql") as f:
        db.executescript(f.read())
