import json
import logging

import requests
from apartments_common import bootstrap, consul, rabbit, storage

from . import routes


def apartment_event_received(ch, method, properties, body):
    data = json.loads(body)
    logging.debug(f"Received {data}")

    if method.routing_key == "added":
        id = data["id"]
        name = data["name"]

        logging.info(f"Adding apartment {name}")
        storage.run_query("INSERT INTO apartments VALUES (?, ?)", (id, name))
    elif method.routing_key == "deleted":
        id = data["id"]
        logging.info(f"Removing apartment {id}")
        storage.run_query("DELETE FROM apartments WHERE id=?", (id,))


def populate_db():
    services = consul.find_services("apartments")
    if len(services) > 0:
        svc = services[0]
        apartments = requests.get(f"http://{svc['address']}:{svc['port']}/apartments?size=999").json()

        for entry in apartments["apartments"]:
            storage.run_query("INSERT INTO apartments VALUES (?, ?)", (entry["id"], entry["name"]))

        logging.info("Database populated")
    else:
        logging.error("Cannot find an available Apartments instance")
        exit(1)


if __name__ == "__main__":
    app = bootstrap.create_app_with_db()
    populate_db()

    rabbit.init_subscribe(
            [{"name": "apartments", "routing_keys": ["added", "deleted"]}],
            apartment_event_received
    )
    rabbit.init_publish("reservations")

    app.register_blueprint(routes.routes)
    bootstrap.start_server(app)
