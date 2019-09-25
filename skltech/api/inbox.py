from contextlib import suppress

from sqlalchemy.orm.exc import NoResultFound
from werkzeug.http import HTTP_STATUS_CODES
from flask import request, url_for, current_app
from flask_restful import Resource, abort

from skltech import models
from skltech.ext import db
from skltech.api.utils import get_user


class InboxMessageRead(Resource):
    def patch(self, user_login, message_id):
        user = get_user(user_login)
        rows = models.Inbox.query.filter_by(user_id=user.user_id, inbox_id=message_id).\
            update({models.Inbox.read: True})
        db.session.commit()
        if rows:
            return {}, 204
        else:
            raise abort(404, message=HTTP_STATUS_CODES[404])


class InboxMessageUnRead(Resource):
    def patch(self, user_login, message_id):
        user = get_user(user_login)
        rows = models.Inbox.query.filter_by(user_id=user.user_id, inbox_id=message_id).\
            update({models.Inbox.read: False})
        db.session.commit()
        if rows:
            return {}, 204
        else:
            raise abort(404, message=HTTP_STATUS_CODES[404])


class InboxMessage(Resource):
    def get(self, user_login, message_id):
        user = get_user(user_login)
        try:
            message = models.Inbox.query.filter_by(user_id=user.user_id, inbox_id=message_id).one()
            return {message.inbox_id: {'subject': message.subject,
                                       'body': message.body,
                                       'from_user': message.from_user,
                                       'to_users': message.to_users,
                                       'read': message.read,
                                       'read-href': url_for('inboxmessageread', user_login=user.user_login,
                                                            message_id=message.inbox_id, _external=True),
                                       'unread-href': url_for('inboxmessageunread', user_login=user.user_login,
                                                              message_id=message.inbox_id, _external=True)}}, 200
        except NoResultFound:
            raise abort(404, message=HTTP_STATUS_CODES[404])

    def delete(self, user_login, message_id):
        user = get_user(user_login)
        rows = models.Inbox.query.filter_by(user_id=user.user_id, inbox_id=message_id).delete()
        db.session.commit()
        if rows:
            return {}, 204
        else:
            raise abort(404, message=HTTP_STATUS_CODES[404])


class Inbox(Resource):
    def get(self, user_login):
        user = get_user(user_login)
        total = db.session.query(db.func.count(models.Inbox.inbox_id)).filter_by(user_id=user.user_id).scalar() or 0
        query = models.Inbox.query.filter_by(user_id=user.user_id).order_by(models.Inbox.inbox_id)
        with suppress(KeyError, ValueError):
            query = query.offset(int(request.args['offset']))
        try:
            query = query.limit(int(request.args['limit']))
        except (KeyError, ValueError):
            query = query.limit(current_app.config['MESSAGES_LIMIT'])
        return {'total': total,
                'data': [{'id': _.inbox_id,
                          'subject': _.subject,
                          'body': _.body,
                          'from_user': _.from_user,
                          'to_users': _.to_users,
                          'read': _.read,
                          'href': url_for('inboxmessage', user_login=user.user_login, message_id=_.inbox_id,
                                          _external=True),
                          'read-href': url_for('inboxmessageread', user_login=user.user_login,
                                               message_id=_.inbox_id, _external=True),
                          'unread-href': url_for('inboxmessageunread', user_login=user.user_login,
                                                 message_id=_.inbox_id, _external=True)}
                         for _ in query.all()]}, 200
