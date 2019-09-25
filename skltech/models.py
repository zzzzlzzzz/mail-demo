from skltech.ext import db


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.Text, nullable=False, unique=True)
    inboxs = db.relationship('Inbox', back_populates='user', cascade='all, delete-orphan')
    sents = db.relationship('Sent', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, user_login):
        self.user_login = user_login


class Inbox(db.Model):
    __tablename__ = 'inbox'

    inbox_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', back_populates='inboxs')
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    from_user = db.Column(db.Text, nullable=False)
    to_users = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, subject, body, from_user, to_users):
        self.subject = subject
        self.body = body
        self.from_user = from_user
        self.to_users = to_users


class Sent(db.Model):
    __tablename__ = 'sent'

    sent_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', back_populates='sents')
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    to_users = db.Column(db.Text, nullable=False)

    def __init__(self, subject, body, to_users):
        self.subject = subject
        self.body = body
        self.to_users = to_users
