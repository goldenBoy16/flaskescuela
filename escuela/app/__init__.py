# from flask import Flask

# from flask_appbuilder.extensions import db
# from .extensions import appbuilder


# def create_app() -> Flask:
#     app = Flask(__name__)
#     app.config.from_object("config")
#     with app.app_context():
#         appbuilder.init_app(app)
#         db.create_all()
#         # Registering the views and APIs
#         ...
#     return app

from flask import Flask
from .extensions import appbuilder, db

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)
    with app.app_context():        
        appbuilder.init_app(app, db.session)        
    return app

app = create_app()