# from flask_appbuilder import AppBuilder

# appbuilder = AppBuilder()

from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
appbuilder = AppBuilder()
csrf = CSRFProtect()