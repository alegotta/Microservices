from apartments_common import bootstrap

from . import routes

if __name__ == "__main__":
    app = bootstrap.create_app()
    app.register_blueprint(routes.routes)

    bootstrap.start_server(app)
