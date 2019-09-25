
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.http import HTTP_STATUS_CODES
from flask_restful import abort

from skltech.models import User


def get_user(user_login):
    """
    Get user by user_login

    :param user_login: User login
    :return: User object
    """
    try:
        return User.query.filter_by(user_login=user_login).one()
    except NoResultFound:
        raise abort(404, message=HTTP_STATUS_CODES[404])
