from api import api
from helper.cache import cache
from helper.function import failed_response, slack_error_notification
from flask import Flask, request
from flask_cors import CORS
import json
import logging
import os
from sqlalchemy.orm import clear_mappers
from werkzeug.exceptions import HTTPException, default_exceptions

app = Flask(__name__)


@app.errorhandler(Exception)
def internal_error(error):
    clear_mappers()
    exception_url = request.url
    method = request.method
    ip = request.remote_addr
    error_log = error.description if isinstance(error, HTTPException) else str(error)
    status_code = error.code if isinstance(error, HTTPException) else 500

    error_message = f"Unexpected HTTP exception(status code: {status_code}): {error_log}" \
        if isinstance(error, HTTPException) \
        else f"Unexpected non-HTTP exception(status code: {status_code}). 카카오톡 채널을 통해 개발팀에 문의해 주시기 바랍니다({error_log})."

    if isinstance(error, HTTPException):  # HTTP error
        slack_error_notification(
            ip=ip,
            type='HTTPException',
            endpoint=exception_url,
            method=method,
            status_code=int(error.code),
            error_message=error_log
        )
        return json.dumps(failed_response(error_message), ensure_ascii=False), status_code
    else:  # non-HTTP error
        slack_error_notification(
            ip=ip,
            type='Non-HTTPException',
            endpoint=exception_url,
            method=method,
            status_code=500,
            error_message=error_log
        )
        return json.dumps(failed_response(error_message), ensure_ascii=False), status_code


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
