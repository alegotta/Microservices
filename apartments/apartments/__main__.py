from apartments_common import bootstrap, rabbit

from . import routes


if __name__ == "__main__":
    app = bootstrap.create_app_with_db()

    rabbit.init_publish("apartments")

    app.register_blueprint(routes.routes)
    bootstrap.start_server(app)
