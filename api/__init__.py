from flask import Blueprint
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api, supports_credentials=True)


from . import board, block, feed, follow, food, login, mission, notice, notification, report, signup, user, version
