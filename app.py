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


@app.errorhandler(500)
def internal_error(error):
    clear_mappers()
    # def error_handling(error):
    #     if isinstance(error, HTTPException):  # HTTP Exeption의 경우
    #         print('here')
    #         result = {
    #             'code': error.code,
    #             'description': error.description,
    #             "message": f"Internal server error: {str(error)}"
    #         }
    #     else:
    #         print('here222')
    #         description = _aborter.mapping[500].description  # 나머지 Exception의 경우
    #         result = {
    #             'code': 500,
    #             'description': description,
    #             "message": f"Internal server error: {str(error)}"
    #         }
    #     resp = json.dumps(result)
    #     # resp.status_code = result['code']
    #     return resp

    result = {
        "result": False,
        "message": f"Internal server error: {str(error)}"
    }
    # result = error_handling(e)
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
