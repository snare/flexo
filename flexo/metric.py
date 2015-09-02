from mongoengine import *

from .template import Exercise
from .app import User


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


class Metric(EmbeddedDocument):
    """
    A measurement of a lift, e.g. Squat 5RM.
    """
    reps = IntField()
    weight = FloatField()
    duration = DateTimeField()
    distance = FloatField()
    estimated = BooleanField()


class MetricGroup(Document):
    """
    A group of metrics for a given exercise, e.g. Squat 1RM, 3RM and 5RM.
    """
    user = ReferenceField(User)
    exercise = ReferenceField(Exercise)
    metrics = ListField(EmbeddedDocumentField(Metric))

    def __init__(self, *args, **kwargs):
        super(MetricGroup, self).__init__(*args, **kwargs)
        self.estimate()

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
