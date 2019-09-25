from contextlib import suppress

from sqlalchemy.orm.exc import NoResultFound
from werkzeug.http import HTTP_STATUS_CODES
from flask import request, url_for, current_app
from flask_restful import Resource, abort

from skltech import models
from skltech.ext import db
from skltech.api.utils import get_user


class SentMessage(Resource):
    def get(self, user_login, message_id):
        user = get_user(user_login)
        try:
            message = models.Sent.query.filter_by(user_id=user.user_id, sent_id=message_id).one()
            return {message.sent_id: {'subject': message.subject,
                                      'body': message.body,
                                      'from_user': user.user_login,
                                      'to_users': message.to_users}}, 200
        except NoResultFound:
            raise abort(404, message=HTTP_STATUS_CODES[404])

    def delete(self, user_login, message_id):
        user = get_user(user_login)
        rows = models.Sent.query.filter_by(user_id=user.user_id, sent_id=message_id).delete()
        db.session.commit()
        if rows:
            return {}, 204
        else:
            raise abort(404, message=HTTP_STATUS_CODES[404])


class Sent(Resource):
    def get(self, user_login):
        user = get_user(user_login)
        total = db.session.query(db.func.count(models.Sent.sent_id)).filter_by(user_id=user.user_id).scalar() or 0
        query = models.Sent.query.filter_by(user_id=user.user_id).order_by(models.Sent.sent_id)
        with suppress(KeyError, ValueError):
            query = query.offset(int(request.args['offset']))
        try:
            query = query.limit(int(request.args['limit']))
        except (KeyError, ValueError):
            query = query.limit(current_app.config['MESSAGES_LIMIT'])
        return {'total': total,
                'data': [{'id': _.sent_id,
                          'subject': _.subject,
                          'body': _.body,
                          'from_user': user.user_login,
                          'to_users': _.to_users,
                          'href': url_for('sentmessage', user_login=user.user_login, message_id=_.sent_id,
                                          _external=True)}
                         for _ in query.all()]}, 200

    def post(self, user_login):
        user = get_user(user_login)
        try:
            subject = request.json['subject']
            body = request.json['body']
            to_users = request.json['to_users']
        except KeyError:
            raise abort(400, message=HTTP_STATUS_CODES[400])
        sent_message = models.Sent(subject, body, to_users)
        user.sents.append(sent_message)
        for to_user_login in to_users.split(';'):
            with suppress(NoResultFound), db.session.begin_nested():
                to_user = models.User.query.filter_by(user_login=to_user_login).one()
                to_user.inboxs.append(models.Inbox(subject, body, user.user_login, to_users))
        db.session.commit()
        return {sent_message.sent_id: {'subject': sent_message.subject,
                                       'body': sent_message.body,
                                       'from_user': user.user_login,
                                       'to_users': sent_message.to_users,
                                       'href': url_for('sentmessage', user_login=user.user_login,
                                                       message_id=sent_message.sent_id, _external=True)}}, 201
