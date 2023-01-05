from api import api
from helper.cache import cache
from helper.function import failed_response, slack_error_notification
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail
import json
import logging
import os
from sqlalchemy.orm import clear_mappers
from werkzeug.exceptions import HTTPException, default_exceptions

app = Flask(__name__)

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

# SMTP configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'circlindev@circlin.co.kr'
app.config['MAIL_PASSWORD'] = 'circlinDev2019!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.mail = mail


@app.errorhandler(Exception)
def internal_error(error):
    clear_mappers()

    if isinstance(error, HTTPException):  # HTTP error
        status_code = error.code
        error_log = error.description
        error_type = "HTTP Exception"
    else:  # non-HTTP error
        status_code = 500
        error_log = str(error)
        error_type = "non-HTTP Exception"

    error_message = f"Unexpected {error_type}(status code: {status_code}): ({error_log}). \n 이 에러가 계속될 경우 카카오톡 채널 '써클인' 으로 문의해 주시기 바랍니다."
    endpoint = request.url
    ip = request.remote_addr
    method = request.method

    slack_error_notification(
        endpoint=endpoint,
        error_message=error_log,
        ip=ip,
        method=method,
        status_code=status_code,
        type=error_type,
    )
    return json.dumps(failed_response(error_message), ensure_ascii=False), status_code


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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.debug = True
    localhost = '127.0.0.1'
    production = '0.0.0.0'
    app.run(host=localhost, debug=True)  # 0.0.0.0 for production or 127.0.0.1 for local development
