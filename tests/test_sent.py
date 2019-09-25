from flask import url_for

from skltech.models import User, Sent, Inbox


def test_sent_get_not_exists(client, database):
    rv = client.get('/messages/test/sent')
    assert rv.status_code == 404


def test_sent_get_empty(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent'.format(user.user_login))
    assert rv.status_code == 200
    assert rv.get_json() == {'total': 0, 'data': []}


def get_sent_ideal(user, sn):
    return {'id': sn.sent_id,
            'subject': sn.subject,
            'body': sn.body,
            'from_user': user.user_login,
            'to_users': sn.to_users,
            'href': url_for('sentmessage', user_login=user.user_login, message_id=sn.sent_id, _external=True)}


def test_sent_get_not_empty(client, database):
    user = User('test')
    sn1 = Sent('Ho', 'Ho ho ho', 'testx;testy')
    user.sents.append(sn1)
    sn2 = Sent('XO', 'Xo ox xo', 'test1;test4')
    user.sents.append(sn2)
    sn3 = Sent('Lo', 'Lo lo lo', 'testw;testz')
    user.sents.append(sn3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3
    assert json['data'][0] == get_sent_ideal(user, sn1)
    assert json['data'][1] == get_sent_ideal(user, sn2)
    assert json['data'][2] == get_sent_ideal(user, sn3)


def test_sent_get_offset(client, database):
    user = User('test')
    sn1 = Sent('Ho', 'Ho ho ho', 'testx;testy')
    user.sents.append(sn1)
    sn2 = Sent('XO', 'Xo ox xo', 'test1;test4')
    user.sents.append(sn2)
    sn3 = Sent('Lo', 'Lo lo lo', 'testw;testz')
    user.sents.append(sn3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent?offset=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3
    assert json['data'][0] == get_sent_ideal(user, sn2)
    assert json['data'][1] == get_sent_ideal(user, sn3)


def test_sent_get_limit(client, database):
    user = User('test')
    sn1 = Sent('Ho', 'Ho ho ho', 'testx;testy')
    user.sents.append(sn1)
    sn2 = Sent('XO', 'Xo ox xo', 'test1;test4')
    user.sents.append(sn2)
    sn3 = Sent('Lo', 'Lo lo lo', 'testw;testz')
    user.sents.append(sn3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent?limit=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3
    assert json['data'][0] == get_sent_ideal(user, sn1)


def test_sent_get_offset_limit(client, database):
    user = User('test')
    sn1 = Sent('Ho', 'Ho ho ho', 'testx;testy')
    user.sents.append(sn1)
    sn2 = Sent('XO', 'Xo ox xo', 'test1;test4')
    user.sents.append(sn2)
    sn3 = Sent('Lo', 'Lo lo lo', 'testw;testz')
    user.sents.append(sn3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent?offset=1&limit=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3
    assert json['data'][0] == get_sent_ideal(user, sn2)


def test_sent_post_not_exists(client, database):
    rv = client.post('/messages/test/sent')
    assert rv.status_code == 404


def test_sent_post_invalid_argument(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.post('/messages/test/sent', json={'subject': 'This is subj', 'body': 'This is body'})
    assert rv.status_code == 400


def test_sent_post(client, database):
    user = User('test')
    database.session.add(user)
    user2 = User('test2')
    database.session.add(user2)
    user3 = User('test3')
    database.session.add(user3)
    database.session.commit()

    msg = {'subject': 'This is subj', 'body': 'This is body', 'to_users': 'test2;notest;test3;nonotest'}

    rv = client.post('/messages/{}/sent'.format(user.user_login), json=msg)
    assert rv.status_code == 201
    created = rv.get_json()
    created_id = list(created.keys())[0]
    created_obj = Sent.query.filter_by(sent_id=created_id, user_id=user.user_id).first()
    created_obj2 = Inbox.query.filter_by(user_id=user2.user_id).first()
    created_obj3 = Inbox.query.filter_by(user_id=user3.user_id).first()
    assert created_obj and created_obj2 and created_obj3
    assert created[created_id]['href'] == url_for('sentmessage', user_login=user.user_login, message_id=created_id, _external=True)
    assert created[created_id]['subject'] == msg['subject'] and \
           created_obj.subject == msg['subject'] and \
           created_obj2.subject == msg['subject'] and \
           created_obj3.subject == msg['subject']
    assert created[created_id]['body'] == msg['body'] and \
           created_obj.body == msg['body'] and \
           created_obj2.body == msg['body'] and \
           created_obj3.body == msg['body']
    assert created[created_id]['from_user'] == user.user_login and \
           created_obj2.from_user == user.user_login and \
           created_obj3.from_user == user.user_login
    assert created[created_id]['to_users'] == msg['to_users'] and \
           created_obj.to_users == msg['to_users'] and \
           created_obj2.to_users == msg['to_users'] and \
           created_obj3.to_users == msg['to_users']


def test_sent_message_get_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent/1'.format(user.user_login))
    assert rv.status_code == 404


def test_sent_message_get(client, database):
    user = User('test')
    sn1 = Sent('This is s', 'THis is body', 'test3;testy')
    user.sents.append(sn1)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/sent/{}'.format(user.user_login, sn1.sent_id))
    assert rv.status_code == 200
    assert rv.get_json() == {str(sn1.sent_id): {'subject': sn1.subject,
                                                'body': sn1.body,
                                                'from_user': user.user_login,
                                                'to_users': sn1.to_users}}


def test_sent_message_delete_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.delete('/messages/{}/sent/1'.format(user.user_login))
    assert rv.status_code == 404


def test_sent_message_delete(client, database):
    user = User('test')
    sn1 = Sent('This is is', 'This body', 'testy;testx')
    user.sents.append(sn1)
    database.session.add(user)
    database.session.commit()

    rv = client.delete('/messages/{}/sent/{}'.format(user.user_login, sn1.sent_id))
    assert rv.status_code == 204
    assert not Sent.query.filter_by(sent_id=sn1.sent_id).first()
