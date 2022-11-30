from . import api
from adapter.database import db_session


from flask import request
import json
from sqlalchemy.orm import clear_mappers