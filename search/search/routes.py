import datetime
import logging

from apartments_common import storage, utils
from flask import Blueprint, request

routes = Blueprint('routes', __name__, url_prefix='/')


@routes.errorhandler(ValueError)
def exception_handler(e):
    logging.warning(f"Validation error: {str(e)}")
    return {"result": False, "error": 1, "description": str(e)}, 400


@routes.get("/up")
@utils.disable_logging
def hello():
    return {"result": True, "description": "Hello World from the search service!"}


@routes.get("/search")
def search():
    params = utils.evaluate_params(request, "start", ("duration", int), ("size", int, 10), ("page", int, 0), ("name", str, ""))
    now = datetime.datetime.now()

    request_date = datetime.datetime.strptime(params["start"], "%Y%m%d")
    if request_date <= now:
        raise ValueError("Invalid date")

    if params["duration"] < 1 or params["duration"] > 60:
        raise ValueError("Invalid duration")
    end_date = request_date + datetime.timedelta(days=params["duration"])
    params["end"] = datetime.datetime.strftime(end_date, "%Y%m%d")

    result = storage.run_query("""
    SELECT DISTINCT a.* FROM apartments as a, reservations as r
    WHERE a.id=r.app_id AND (end<? OR start>=?) AND a.name LIKE ?
    LIMIT ?,?
    """, (params["start"], params["end"], f"%{params['name']}%", params["size"]*params["page"], params["size"]))

    return {"apartments": result}
