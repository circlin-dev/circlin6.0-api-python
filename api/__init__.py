from flask import Blueprint
from flask_cors import CORS

api = Blueprint('api', __name__)
CORS(api, supports_credentials=True)
