import logging
import os

from flask import Flask

from . import consul, storage, rabbit


def create_app_with_db():
    storage.init_db()
    return create_app()


def create_app():
    setup_logging()
    logging.info(f"Starting {os.environ['SVC_TYPE']}")
    app = Flask(__name__)

    consul.register(os.environ["SVC_TYPE"])
    app.teardown_appcontext(storage.close_db)

    return app


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("sqlite3").setLevel(logging.WARNING)


def start_server(app):
    try:
        logging.info("Starting the web server")
        app.run(host="0.0.0.0", threaded=True)
    finally:
        consul.deregister()
        rabbit.disconnect()
