git addfrom mongoengine import *
from nose.tools import *
import yaml
import flexo
from flexo import *
from flexo.exercise import *
from flexo.metric import *
from flexo.program import *
from flexo.weight import *
from pprint import pprint as pp

db = None
d = None


def setup():
    global db, u, d
    db = connect('testdb', host='192.168.99.100')
    # u = User(name="testuser", password="test").save()
    # d = yaml.load(file("tests/test.yaml").read())


def teardown():
    db.drop_database('testdb')


def test_max_calc():
    mc = MaxCalc(5, 100.0)
    assert [mc.estimate(i) for i in range(1, 11)] == [116.5, 109.28705440900562, 106.00545950864422, 102.91519434628977,
                                                      100.0, 97.24540901502505, 94.63850528025995, 92.16772151898734,
                                                      89.82266769468004, 87.59398496240601]


def test_metric():
    m = Metric(reps=5, weight=100)
    assert m.reps == 5
    assert m.weight == 100
    assert Metric(reps=5, weight="100kg").weight == 100
    assert Metric(reps=5, weight="100lb").weight == 45.5


def test_metric_group():
    global mg
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
    assert mg.metrics[2].weight == 106
    assert mg[5].reps == 5
    assert mg[5].weight == 100.0
    assert mg[1].reps == 1
    assert mg[1].weight == 116.5
    assert mg[3].reps == 3
    assert mg[3].weight == 106
    mg[2] = 110
    assert mg[2].weight == 110
    mg[2] = "110lb"
    assert mg[2].weight == 50


def test_metric_set():
    squat = Exercise(name='Squat')
    bench = Exercise(name='Bench')
    s = MetricSet(groups=[
        MetricGroup(exercise=bench, metrics=[
            Metric(reps=1, weight="120kg"),
            Metric(reps=3, estimated=True)]),
        MetricGroup(exercise=squat, metrics=[
            Metric(reps=1, weight="150kg"),
            Metric(reps=3, estimated=True)])
    ])
    assert s.groups[0].exercise == bench
    assert s.groups[0].metrics[0].reps == 1
    assert s.groups[0].metrics[0].weight == 120
    assert s.groups[1].metrics[0].reps == 1
    assert s.groups[1].metrics[0].weight == 150
    assert s.groups[0].metrics[1].weight == 109


def test_expr():
    mg = MetricGroup(exercise=Exercise(name='Squat'), metrics=[
        Metric(reps=5, weight=100.0),
        Metric(reps=1, estimated=True),
        Metric(reps=3, estimated=True)])

    assert WeightExpr("100% of 5RM", metric_group=mg).eval() == 100
    assert int(WeightExpr("100% of 5RM", metric_group=mg)) == 100
    assert float(WeightExpr("100% of 5RM", metric_group=mg)) == 100.0
    assert WeightExpr("100% of 1RM", metric_group=mg).eval() == 116.5
    assert int(WeightExpr("100% of 1RM", metric_group=mg)) == 116
    assert float(WeightExpr("100% of 1RM", metric_group=mg)) == 116.5
    assert int(WeightExpr("100% of 3RM", metric_group=mg)) == 106
    assert WeightExpr("100% of 3RM", metric_group=mg) == 106
    assert WeightExpr("70% of 1RM", metric_group=mg) == 81.5
    assert WeightExpr("70% of 1RM + 10", metric_group=mg) == 91.5
    assert WeightExpr("70% of (1RM + 10)", metric_group=mg) == 88.5
    assert WeightExpr("1RM + 10 - 0.7 * 1RM", metric_group=mg) == 45
    assert WeightExpr("70% of (1RM + 10)", metric_group=mg, resolution=0.01) == 88.55

    assert WeightExpr("50kg") == 50
    assert WeightExpr("50lb") == 22.5
    assert WeightExpr("70% of 5RM + 10kg", metric_group=mg) == 80
    assert WeightExpr("70% of 5RM + 10lb", metric_group=mg) == 74.5


def test_set_group():
    bench = Exercise('bench')
    mg = MetricGroup(exercise=bench, metrics=[Metric(reps=1, weight=100.0), Metric(reps=3, estimated=True)])

    s = SetGroup(exercise=bench, autogen=True, sets=3, reps=8, weight='70kg')
    s.generate()
    assert len(s.children) == 3
    assert s.children[0].reps == 8
    assert s.children[0].weight == 70

    s = SetGroup(exercise=Exercise('bench'), autogen=True, sets=3, reps=8, weight='50% of 1RM')
    s.generate(metric_group=mg)
    assert len(s.children) == 3
    assert s.children[0].reps == 8
    assert s.children[0].weight == 50


def render_program_text(p):
    print p.name


def test_program_simple():
    bench = Exercise("bench")
    squat = Exercise("squat")
    deadlift = Exercise("deadlift")

    s = MetricSet(groups=[
        MetricGroup(exercise=bench, metrics=[
            Metric(reps=1, weight="120kg"),
            Metric(reps=3, estimated=True)]),
        MetricGroup(exercise=squat, metrics=[
            Metric(reps=1, weight="150kg"),
            Metric(reps=3, estimated=True)])
    ])

    p = Program(
        metrics=s,
        name="simple program",
        children=[
            Workout(name="day 1", children=[
                SetGroup(exercise=bench, autogen=True, sets=5, reps=5, weight="60kg"),
                SetGroup(exercise=squat, autogen=True, sets=5, reps=5, weight="100kg"),
            ]),
            Workout(name="day 2", children=[
                SetGroup(exercise=bench, autogen=True, sets=8, reps=3, weight="70kg"),
                SetGroup(exercise=deadlift, autogen=True, sets=2, reps=6, weight="100kg"),
            ]),
        ]
    )

    assert p.name == 'simple program'
    assert len(p.children) == 2
    assert p.children[0].name == 'day 1'
    assert p.children[0].children[0].exercise == bench
    assert p.children[0].children[0].sets == 5
    assert p.children[0].children[0].reps == 5
    assert p.children[0].children[0].weight == 60
    assert p.children[0].children[1].exercise == squat
    assert p.children[0].children[1].sets == 5
    assert p.children[0].children[1].reps == 5
    assert p.children[0].children[1].weight == 100
    assert p.children[1].children[0].exercise == bench
    assert p.children[1].children[0].sets == 8
    assert p.children[1].children[0].reps == 3
    assert p.children[1].children[0].weight == 70
    assert p.children[1].children[1].exercise == deadlift
    assert p.children[1].children[1].sets == 2
    assert p.children[1].children[1].reps == 6
    assert p.children[1].children[1].weight == 100

    print_program(p)


def test_program_smolov():
    bench = Exercise("bench")
    p = Program(
        name="smolov jr",
        metrics=MetricSet(groups=[
            MetricGroup(exercise=bench, metrics=[
                Metric(reps=1, weight="120kg"),
                Metric(reps=3, estimated=True)])
        ]),
        variables={'increment': '10kg'},
        children=[
            Block(name="week 1", children=[
                Workout(name="day 1", children=[
                    SetGroup(exercise=bench, children=[
                        SetGroup(name="warmup", autogen=True, reps=5, bottom="20kg", top="70% of 1RM - 1", increment="20kg"),
                        SetGroup(name="work", autogen=True, sets=6, reps=6, weight="70% of 1RM"),
                    ])
                ]),
                Workout(name="day 2", children=[
                    SetGroup(exercise=bench, children=[
                        SetGroup(name="warmup", autogen=True, reps=5, bottom="20kg", top="75% of 1RM - 1", increment="20kg"),
                        SetGroup(name="work", autogen=True, sets=7, reps=5, weight="75% of 1RM"),
                    ])
                ]),
                Workout(name="day 3", children=[
                    SetGroup(exercise=bench, children=[
                        SetGroup(name="warmup", autogen=True, reps=5, bottom="20kg", top="80% of 1RM - 1", increment="20kg"),
                        SetGroup(name="work", autogen=True, sets=8, reps=4, weight="80% of 1RM"),
                    ])
                ]),
                Workout(name="day 4", children=[
                    SetGroup(exercise=bench, children=[
                        SetGroup(name="warmup", autogen=True, reps=5, bottom="20kg", top="80% of 1RM - 1", increment="20kg"),
                        SetGroup(name="work", autogen=True, sets=10, reps=3, weight="85% of 1RM"),
                    ])
                ]),
            ]),
        ]
    )

    p.generate()

    assert p.name == 'smolov jr'
    assert p.variables == {'increment': '10kg'}
    assert len(p.children) == 1
    assert len(p.children[0].children) == 4
    assert [len(w.children) for w in p.children[0].children] == [1, 1, 1, 1]
    assert p.children[0].name == 'week 1'
    assert p.children[0].children[0].name == 'day 1'
    assert p.children[0].children[0].children[0].exercise == bench

    assert len(p.children[0].children[0].children[0].children[1].children) == 6
    assert set([s.reps for s in p.children[0].children[0].children[0].children[1].children]) == set([6])
    assert set([s.weight for s in p.children[0].children[0].children[0].children[1].children]) == set([84.0])

    print_program(p)


def test_program_smolov_yaml():
    pass
