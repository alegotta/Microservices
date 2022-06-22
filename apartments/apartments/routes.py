import json
import logging
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
    return {"result": True, "description": "Hello World from the apartments service!"}


@routes.get("/add")
def add():
    params = utils.evaluate_params(request, "name", ("size", int))
    if params["size"] < 1 or params["size"] > 1000:
        raise ValueError("Wrong square meters parameter")

    already_exists = storage.run_query("SELECT id FROM apartments WHERE name = ?", (params["name"],))
    if (len(already_exists)) > 0:
        raise ValueError("Cannot proceed because this apartment already exists")

    id = str(uuid.uuid4())
    storage.run_query("INSERT INTO apartments VALUES (?, ?, ?)",
                      (id, params["name"], params["size"]))

    result = {**params, "id": id}
    rabbit.publish("apartments", "added", json.dumps(result))
    logging.info(f"Added apartment {result}")

    return result, 201


@routes.get("/delete")
def delete():
    params = utils.evaluate_params(request, "name")

    app_to_remove = storage.run_query("SELECT * FROM apartments WHERE name=?", (params["name"],))
    if len(app_to_remove) == 0:
        raise ValueError(f"The apartment {params['name']} was not found")

    app_to_remove = app_to_remove[0]
    storage.run_query("DELETE FROM apartments WHERE name=?", (app_to_remove["name"],))
    rabbit.publish("apartments", "deleted", json.dumps(app_to_remove))
    logging.info(f"Deleted apartment {app_to_remove}")

    return {"result": True}


@routes.get("/apartments")
def apartments():
    params = utils.evaluate_params(request, ("size", int, 10), ("page", int, 0))

    result = storage.run_query("SELECT * FROM apartments LIMIT ?,?",
                               (params["size"]*params["page"], params["size"]))
    return {"apartments": result}
