from api import api
from helper.cache import cache
from flask import Flask
from flask_cors import CORS
import json
import logging
import os
from sqlalchemy.orm import clear_mappers
from werkzeug.exceptions import HTTPException, default_exceptions, _aborter

app = Flask(__name__)


@app.errorhandler(Exception)
def internal_error(error):
    clear_mappers()
    if isinstance(error, HTTPException):  # HTTP error
        result = {
            "result": False,
            "error": f"Unexpected HTTP exception(error code: {error.code}): {error.description}"
        }
        return json.dumps(result, ensure_ascii=False), error.code
    else:  # non-HTTP error
        result = {
            "result": False,
            "error": f"Unexpected non-HTTP exception(error code: 500). 카카오톡 채널을 통해 개발팀에 문의해 주시기 바랍니다({str(error)})."
        }
        return json.dumps(result, ensure_ascii=False), 500


# Cache configuration
cache_config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
    "CACHE_DIR": os.getenv("CACHE_DIR") or f"./_cache",
    "CACHE_DEFAULT_TIMEOUT": 5 * 60
}
cache.init_app(app=app, config=cache_config)


# CORS configuration
CORS(app, supports_credentials=True)


# API configuration
app.register_blueprint(api, url_prefix='/api')


# Logging configuration    # Deactivate here at development environment
logging.basicConfig(filename='./' + 'execution_log.log', filemode='a+',
                    format=' [%(filename)s:%(lineno)s:%(funcName)s()]- %(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


@app.route('/')
def hello_world():
    return "Hello, CIRCLIN6.0~!!"


if __name__ == '__main__':
    app.debug = True
    localhost = '127.0.0.1'
    production = '0.0.0.0'
    app.run(host=localhost, debug=True)  # 0.0.0.0 for production or 127.0.0.1 for local development
