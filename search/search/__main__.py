import json
import logging

import requests
from apartments_common import bootstrap, consul, rabbit, storage

from . import routes


def messages_callback(ch, method, properties, body):
    data = json.loads(body)
    logging.debug(f"Received {data}")

    if method.exchange == "apartments":
        apartments_callback(ch, method, properties, data)
    elif method.exchange == "reservations":
        reservations_callback(ch, method, properties, data)


def apartments_callback(ch, method, properties, data):
    if method.routing_key == "added":
        id = data["id"]
        name = data["name"]

        logging.info(f"Adding apartment {name}")
        storage.run_query("INSERT INTO apartments VALUES (?, ?)", (id, name))

    elif method.routing_key == "deleted":
        id = data["id"]
        logging.info(f"Removing apartment {id}")
        storage.run_query("DELETE FROM apartments WHERE id=?", (id,))


def reservations_callback(ch, method, properties, data):
    if method.routing_key == "added":
        storage.run_query(
            """
            INSERT INTO reservations(id, app_id, start, end)
            VALUES(?, ?, ?, ?);
        """, (data["id"], data["app_id"], data["start"], data["end"]))

        logging.info(f"Adding reservation {data['id']}")

    elif method.routing_key == "deleted":
        id = data["id"]
        logging.info(f"Removing reservation {id}")
        storage.run_query("DELETE FROM reservations WHERE ID=?", (id,))


def populate_db(type):
    services = consul.find_services(type)
    if len(services) > 0:
        svc = services[0]
        results = requests.get(
            f"http://{svc['address']}:{svc['port']}/{type}?size=999").json()

        for entry in results[type]:
            if type == "apartments":
                storage.run_query(
                    "INSERT INTO apartments VALUES (?, ?)", (entry["id"], entry["name"]))
            elif type == "reservations":
                storage.run_query("INSERT INTO reservations(id, app_id, start, end) VALUES(?, ?, ?, ?);",
                                  (entry["id"], entry["app_id"], entry["start"], entry["end"]))

        logging.info("Database populated")
    else:
        logging.error(f"Cannot find an available {type} instance")
        exit(1)


if __name__ == "__main__":
    app = bootstrap.create_app_with_db()

    populate_db("apartments")
    populate_db("reservations")

    rabbit.init_subscribe(
        [{"name": "apartments", "routing_keys": ["added", "deleted"]},
         {"name": "reservations", "routing_keys": ["added", "deleted"]}],
        messages_callback
    )

    app.register_blueprint(routes.routes)
    bootstrap.start_server(app)
