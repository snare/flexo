import json
from mongoengine import *
from flask.ext.mongoengine import MongoEngine

import flexo
from flexo import create_app, User, Exercise, MetricGroup, Metric

u = None
c = None
app = None


def setup():
    global app, u, c
    app = create_app({"MONGODB_SETTINGS": {
        'db': 'testdb',
        'host': '192.168.99.100'
    }})
    c = app.test_client()
    u = User(name="testuser", password="test")
    u.save()


def teardown():
    app.db.connection.drop_database('testdb')


def test_login_missing():
    assert json.loads(c.get('/api/login').data) == {'ok': False, 'info': 'Missing creds'}


def test_login_fail():
    d = json.loads(c.post('/api/login', data=json.dumps({'name': 'testuser', 'password': 'xxx'}),
                          headers={'Content-type': 'application/json'}).data)
    assert d == {'ok': False, 'info': 'Authentication failed'}


def test_login_success():
    d = json.loads(c.post('/api/login', data=json.dumps({'name': 'testuser', 'password': 'test'}),
                          headers={'Content-type': 'application/json'}).data)
    assert d == {'ok': True, 'name': 'testuser', 'info': 'Successful authentication'}


def test_metric_group():
    squat = Exercise(name='Squat').save()
    mg = MetricGroup(exercise=squat, metrics=[
        Metric(reps=5, weight=100.0),
        Metric(reps=1, estimated=True),
        Metric(reps=3, estimated=True)],
        user=u)
    mg.save()
    d = json.loads(c.get('/api/metric').data)
    assert len(d) == 1
    assert len(d[0]['metrics']) == 3
    assert str(d[0]['user']['$oid']) == str(u.id)
    squat.delete()
    mg.delete()


def test_exercises():
    Exercise(name='Bench press').save()
    Exercise(name='Deadlift').save()
    Exercise(name='Overhead press').save()
    assert len(json.loads(c.get('/api/exercise').data)) == 3
