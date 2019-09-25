from os import environ

from werkzeug.http import HTTP_STATUS_CODES
from flask import Flask, jsonify, current_app

from skltech.ext import db
from skltech import api


def create_app():
    """
    Factory for application

    :return: application instance
    """
    app = Flask(__name__)
    app.config.from_object(environ.get('SKLTECH_CONFIG', 'config.ProductionConfig'))
    db.init_app(app)
    api.init_app(app)

    @app.errorhandler(Exception)
    def unhandled_exception(_):
        current_app.logger.exception('unhandled_exception')
        db.session.rollback()
        return jsonify({'code': 500, 'message': HTTP_STATUS_CODES[500]}), 500

    return app
