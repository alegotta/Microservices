import logging
import requests

from apartments_common import consul, utils
from flask import Blueprint, request


routes = Blueprint('routes', __name__)
services = None


def get_services():
    global services
    if services is None:
        services = {
            "apartments": consul.find_services("apartments"),
            "reservations": consul.find_services("reservations"),
            "search": consul.find_services("search")
        }

        if any(service for service in services.values()) is None:
            logging.error(f"Cannot find available services: {services}")
            exit(1)

    return services


@routes.get("/up")
@utils.disable_logging
def hello():
    return {"result": True, "description": "Hello World from the gateway service!"}


@routes.get("/<service>/<method>")
def redirect(service, method):
    if service not in ("apartments", "reservations", "search"):
        return {"result": False, "description": "The service does not exist!"}

    service = get_services()[service][0]
    request_string = f"http://{service['address']}:{service['port']}/{method}?{request.query_string.decode()}"
    return requests.get(request_string).json()
