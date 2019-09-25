from skltech.ext import rest
from skltech.api.sent import Sent, SentMessage
from skltech.api.inbox import Inbox, InboxMessage, InboxMessageRead, InboxMessageUnRead


def init_app(app):
    """
    Register api endpoints

    :param app: Flask application
    :return: None
    """
    rest.add_resource(Sent, '/messages/<user_login>/sent')
    rest.add_resource(SentMessage, '/messages/<user_login>/sent/<int:message_id>')
    rest.add_resource(Inbox, '/messages/<user_login>/inbox')
    rest.add_resource(InboxMessage, '/messages/<user_login>/inbox/<int:message_id>')
    rest.add_resource(InboxMessageRead, '/messages/<user_login>/inbox/<int:message_id>/read')
    rest.add_resource(InboxMessageUnRead, '/messages/<user_login>/inbox/<int:message_id>/unread')
    rest.init_app(app)
