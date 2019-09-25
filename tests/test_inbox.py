from flask import url_for

from skltech.models import User, Inbox


def test_inbox_get_not_exists(client, database):
    rv = client.get('/messages/test/inbox')
    assert rv.status_code == 404


def test_inbox_get_empty(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()
    rv = client.get('/messages/{}/inbox'.format(user.user_login))
    assert rv.status_code == 200
    assert rv.get_json() == {'data': [], 'total': 0}


def get_inbox_ideal(user, ib):
    return {'id': ib.inbox_id,
            'subject': ib.subject,
            'body': ib.body,
            'from_user': ib.from_user,
            'to_users': ib.to_users,
            'read': ib.read,
            'href': url_for('inboxmessage', user_login=user.user_login, message_id=ib.inbox_id, _external=True),
            'read-href': url_for('inboxmessageread', user_login=user.user_login, message_id=ib.inbox_id, _external=True),
            'unread-href': url_for('inboxmessageunread', user_login=user.user_login, message_id=ib.inbox_id, _external=True)}


def test_inbox_get_not_empty(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body this body 1', 'test', 'testx;testy;testz')
    user.inboxs.append(ib1)
    ib2 = Inbox('Subj2', 'Body this body 2', 'test', 'testa;testb')
    user.inboxs.append(ib2)
    ib3 = Inbox('Subj3', 'Body this body 3', 'test', 'testxx;testyy')
    user.inboxs.append(ib3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/inbox'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3 and len(json['data']) == 3
    assert json['data'][0] == get_inbox_ideal(user, ib1)
    assert json['data'][1] == get_inbox_ideal(user, ib2)
    assert json['data'][2] == get_inbox_ideal(user, ib3)


def test_inbox_get_offset(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body this body 1', 'test', 'testx;testy;testz')
    user.inboxs.append(ib1)
    ib2 = Inbox('Subj2', 'Body this body 2', 'test', 'testa;testb')
    user.inboxs.append(ib2)
    ib3 = Inbox('Subj3', 'Body this body 3', 'test', 'testxx;testyy')
    user.inboxs.append(ib3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/inbox?offset=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3 and len(json['data']) == 2
    assert json['data'][0] == get_inbox_ideal(user, ib2)
    assert json['data'][1] == get_inbox_ideal(user, ib3)


def test_inbox_get_limit(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body this body 1', 'test', 'testx;testy;testz')
    user.inboxs.append(ib1)
    ib2 = Inbox('Subj2', 'Body this body 2', 'test', 'testa;testb')
    user.inboxs.append(ib2)
    ib3 = Inbox('Subj3', 'Body this body 3', 'test', 'testxx;testyy')
    user.inboxs.append(ib3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/inbox?limit=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3 and len(json['data']) == 1
    assert json['data'][0] == get_inbox_ideal(user, ib1)


def test_inbox_get_offset_limit(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body this body 1', 'test', 'testx;testy;testz')
    user.inboxs.append(ib1)
    ib2 = Inbox('Subj2', 'Body this body 2', 'test', 'testa;testb')
    user.inboxs.append(ib2)
    ib3 = Inbox('Subj3', 'Body this body 3', 'test', 'testxx;testyy')
    user.inboxs.append(ib3)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/inbox?offset=1&limit=1'.format(user.user_login))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json['total'] == 3 and len(json['data']) == 1
    assert json['data'][0] == get_inbox_ideal(user, ib2)


def test_inbox_message_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{0}/inbox/1'.format(user.user_login))
    assert rv.status_code == 404


def test_inbox_message(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body of this', 'root', 'test;testy')
    user.inboxs.append(ib1)
    database.session.add(user)
    database.session.commit()

    rv = client.get('/messages/{}/inbox/{}'.format(user.user_login, ib1.inbox_id))
    json = rv.get_json()
    assert rv.status_code == 200
    assert json == {str(ib1.inbox_id):
                        {'subject': ib1.subject,
                         'body': ib1.body,
                         'from_user': ib1.from_user,
                         'to_users': ib1.to_users,
                         'read': ib1.read,
                         'read-href': url_for('inboxmessageread', user_login=user.user_login, message_id=ib1.inbox_id, _external=True),
                         'unread-href': url_for('inboxmessageunread', user_login=user.user_login, message_id=ib1.inbox_id, _external=True)
                         }}


def test_inbox_message_delete_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.delete('/messages/{}/inbox/1'.format(user.user_login))
    assert rv.status_code == 404


def test_inbox_message_delete(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body of body', 'koor', 'test;testa;testb;testc')
    user.inboxs.append(ib1)
    database.session.add(user)
    database.session.commit()

    rv = client.delete('/messages/{}/inbox/{}'.format(user.user_login, ib1.inbox_id))
    assert rv.status_code == 204
    assert not Inbox.query.filter_by(inbox_id=ib1.inbox_id).first()


def test_inbox_message_read_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.patch('/messages/{}/inbox/1/read'.format(user.user_login))
    assert rv.status_code == 404


def test_inbox_message_read(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body fo body', 'yum', 'test;test1;test5')
    ib1.read = False
    user.inboxs.append(ib1)
    database.session.add(user)
    database.session.commit()

    rv = client.patch('/messages/{}/inbox/{}/read'.format(user.user_login, ib1.inbox_id))
    assert rv.status_code == 204
    assert Inbox.query.filter_by(inbox_id=ib1.inbox_id).first().read


def test_inbox_message_unread_not_exists(client, database):
    user = User('test')
    database.session.add(user)
    database.session.commit()

    rv = client.patch('/messages/{}/inbox/1/unread'.format(user.user_login))
    assert rv.status_code == 404


def test_inbox_message_unread(client, database):
    user = User('test')
    ib1 = Inbox('Subj1', 'Body fo body', 'yum', 'test;test1;test5')
    ib1.read = True
    user.inboxs.append(ib1)
    database.session.add(user)
    database.session.commit()

    rv = client.patch('/messages/{}/inbox/{}/unread'.format(user.user_login, ib1.inbox_id))
    assert rv.status_code == 204
    assert not Inbox.query.filter_by(inbox_id=ib1.inbox_id).first().read
