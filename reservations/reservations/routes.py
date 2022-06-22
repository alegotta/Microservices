import datetime
import json
import logging
import sqlite3
import uuid

from apartments_common import rabbit, storage, utils
from flask import Blueprint, request

routes = Blueprint('routes', __name__, url_prefix='/')


@routes.errorhandler(ValueError)
def exception_handler(e):
    logging.warning(f"Validation error: {str(e)}")
    return {"result": False, "description": str(e)}, 400


@routes.get("/up")
@utils.disable_logging
def hello():
    return {"result": True, "description": "Hello World from the reservations service!"}


@routes.get("/add")
def add():
    params = utils.evaluate_params(request, "app_id", "start", ("duration", int), ("vip", int, 0))

    id = str(uuid.uuid4())
    now = datetime.datetime.now()
    if params["vip"] != 1:
        params["vip"] = 0

    request_date = datetime.datetime.strptime(params["start"], "%Y%m%d")
    if request_date <= now:
        raise ValueError("Invalid date")

    if params["duration"] < 1 or params["duration"] > 60:
        raise ValueError("Invalid duration")
    end_date = request_date + datetime.timedelta(days=params["duration"]-1)
    params["end"] = datetime.datetime.strftime(end_date, "%Y%m%d")

    conflicts = storage.run_query(
        """
        SELECT * FROM reservations
        WHERE app_id=? AND (end>=? AND start<?);
    """, (params["app_id"], params["start"], params["end"]))

    if len(conflicts) > 0:
        return {"error": 4, "result": False, "description": "The apartment is already booked!"}, 400

    try:
        storage.run_query(
            """
            INSERT INTO reservations(id, app_id, start, end, vip)
            VALUES(?, ?, ?, ?, ?);
        """, (id, params["app_id"], params["start"], params["end"], params["vip"]))
    except sqlite3.IntegrityError:
        return {"error": 4, "result": False, "description": "The apartment does not exist!"}, 400

    result = {"id": id, **params}
    rabbit.publish("reservations", "added", json.dumps(result))
    logging.info(f"Added reservation {result}")

    return result


@routes.get("/delete")
def delete():
    params = utils.evaluate_params(request, "id")

    storage.run_query("DELETE FROM reservations WHERE id=?", (params["id"],))
    rabbit.publish("reservations", "deleted", json.dumps({"id": params["id"]}))
    logging.info(f"Removed reservation {params}")

    return {"result": True}


@routes.get("/reservations")
def reservations():
    params = utils.evaluate_params(request, ("size", int, 10), ("page", int, 0))

    result = storage.run_query("SELECT * FROM reservations LIMIT ?,?", (params["size"]*params["page"], params["size"]))
    return {"reservations": result}
