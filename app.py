from api import api
from flask import Flask, request
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Logging configuration
logging.basicConfig(filename='./' + 'execution_log.log', filemode='a+',
                    format=' [%(filename)s:%(lineno)s:%(funcName)s()]- %(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


# API configuration
app.register_blueprint(api, url_prefix='/api')


@app.route('/')
def hello_world():
    return "Hello, CIRCLIN6.0!"


if __name__ == '__main__':
    localhost = '127.0.0.1'
    production = '0.0.0.0'
    app.run(host=localhost, debug=True)  # 0.0.0.0 for production or 127.0.0.1 for local development
