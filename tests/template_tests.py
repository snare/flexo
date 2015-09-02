from mongoengine import *
from nose.tools import *

import flexo
from flexo import *

db = None


def setup():
    global db, u
    db = connect('testdb')
    u = User(name="testuser", password="test").save()


def teardown():
    db.drop_database('testdb')


def test_max_calc():
    mc = MaxCalc(5, 100.0)
    assert [mc.estimate(i) for i in range(1, 11)] == [116.5, 109.28705440900562, 106.00545950864422, 102.91519434628977, 100.0,
                                                      97.24540901502505, 94.63850528025995, 92.16772151898734,
                                                      89.82266769468004, 87.59398496240601]


def test_metric_group():
    squat = Exercise(name='Squat')
    mg = MetricGroup(exercise=squat, metrics=[
        Metric(reps=5, weight=100.0),
        Metric(reps=1, estimated=True),
        Metric(reps=3, estimated=True)])
    assert mg.metrics[0].reps == 5
    assert mg.metrics[0].weight == 100.0
    assert mg.metrics[1].reps == 1
    assert mg.metrics[1].weight == 116.5
    assert mg.metrics[2].reps == 3
    assert mg.metrics[2].weight == 106.00545950864422


def test_template():
    t = Template(user=u).save()
