import json
from mongoengine import *

import flexo
from flexo import app, User

c = app.test_client()


def setup():
    global db, u
    db = connect('testdb')
    u = User(name="testuser", password="test").save()


def teardown():
    db.drop_database('testdb')


def test_login_missing():
    assert json.loads(c.get('/login').data) == {'ok': False, 'info': 'Missing creds'}


def test_login_fail():
    d = json.loads(c.post('/login', data=json.dumps({'name': 'testuser', 'password': 'xxx'}),
                          headers={'Content-type': 'application/json'}).data)
    assert d == {'ok': False, 'info': 'Authentication failed'}


def test_login_success():
    d = json.loads(c.post('/login', data=json.dumps({'name': 'testuser', 'password': 'test'}),
                          headers={'Content-type': 'application/json'}).data)
    assert d == {'ok': True, 'name': 'testuser', 'info': 'Successful authentication'}
