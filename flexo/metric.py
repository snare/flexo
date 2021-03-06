from mongoengine import *

from .user import User
from .weight import WeightMixin
from .exercise import *


class MaxCalc(object):
    """
    Estimate rep maxes based on the available info.
    """
    coefficients = [1.000, 1.066, 1.099, 1.132, 1.165, 1.198, 1.231, 1.264, 1.297, 1.330]

    def __init__(self, reps=0, weight=0):
        if reps:
            self.prime(reps, weight)

    def prime(self, reps=0, weight=0):
        """
        Estimate a 1RM based on the given rep max.
        """
        if reps == 1:
            self.onerm = weight
        else:
            self.onerm = (weight * reps * 0.033) + weight

    def estimate(self, reps):
        """
        Estimate a max for the given rep count.
        """
        return self.onerm / MaxCalc.coefficients[reps - 1]


class Metric(WeightMixin, EmbeddedDocument):
    """
    A measurement of a lift, e.g. Squat 5RM.
    """
    reps = IntField()
    weight_expr = StringField()
    duration = DateTimeField()
    distance = FloatField()
    estimated = BooleanField()
    type = StringField()

    def __repr__(self):
        return "Metric(reps={}, weight_expr={}, duration={}, distance={}, estimated={})".format(
            self.reps, self.weight_expr, self.duration, self.distance, self.estimated)


class MetricGroup(EmbeddedDocument):
    """
    A group of metrics for a given exercise, e.g. Squat 1RM, 3RM and 5RM.
    """
    exercise = ReferenceField(Exercise)
    metrics = ListField(EmbeddedDocumentField(Metric))

    def __init__(self, dict=None, *args, **kwargs):
        super(MetricGroup, self).__init__(*args, **kwargs)
        self.estimate()

    def __getitem__(self, key):
        [metric] = (m for m in self.metrics if m.reps == key)
        return metric

    def __setitem__(self, key, value):
        ms = [m for m in self.metrics if m.reps == key]
        if len(ms):
            ms[0].weight = value
        else:
            self.add_metric(Metric(reps=key, weight=value))

    def estimate(self):
        """
        Update estimated metrics.
        """
        m = sorted([m for m in self.metrics if not m.estimated], key=lambda m: m.reps)
        if len(m):
            mc = MaxCalc(m[0].reps, m[0].weight)
            for m in self.metrics:
                if m.estimated:
                    m.weight = mc.estimate(m.reps)

    def add_metric(self, metric):
        """
        Add a metric to the group.
        """
        self.metrics.append(metric)
        self.estimate()

    def remove_metric(self, metric):
        """
        Remove a metric from the group
        """
        self.metrics.remove(metric)
        self.estimate()


class MetricSet(EmbeddedDocument):
    """
    A set of MetricGroups. Used to collect metrics for multiple exercises
    together to apply to a program.
    """
    groups = ListField(EmbeddedDocumentField(MetricGroup))

    def __getitem__(self, key):
        [g] = (g for g in self.groups if g.exercise == key or g.exercise.name == key)
        return g
