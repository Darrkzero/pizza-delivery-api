from flask import Flask
from flask_restx import Api
from .auth.views import auth_namespace
from .order.views import order_namespace
from.config.config import config_dict
from .utils import db
from .models.order import Order
from .models.user import User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
def create_app(config = config_dict['dev']):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    api= Api(app)

    
    api.add_namespace(auth_namespace)
    api.add_namespace(order_namespace)

    @app.shell_context_processor
    def make_shell_context():
        return{
            "db":db,
            "User":User,
            "Order":Order
        }
    return app