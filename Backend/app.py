from flask import Flask
from flask_migrate import Migrate
from models import db,TokenBlocklist
from flask_cors import CORS
from datetime import timedelta
from flask_jwt_extended import JWTManager


app = Flask(__name__)

CORS(app)
# migration initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conn.db'
migrate = Migrate(app, db)
db.init_app(app)

# Jwt
app.config["JWT_SECRET_KEY"] = "dgsjfgfgfeyyeyud" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] =  timedelta(hours=1)

jwt = JWTManager(app)
jwt.init_app(app)

from views import *


# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None
