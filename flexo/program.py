from mongoengine import *
from .user import User
from .weight import WeightMixin, WeightExpr
from .metric import *
from .exercise import *


class Set(WeightMixin, EmbeddedDocument):
    """
    A set of an exercise.
    """
    name = StringField()
    reps = IntField()
    weight_expr = StringField()
    rpe = FloatField()
    duration = DateTimeField()
    distance = FloatField()

    def __str__(self):
        return "Set(reps={}, weight_expr={})".format(self.reps, self.weight_expr)

    def __init__(self, *args, **kwargs):
        super(Set, self).__init__(*args, **kwargs)

    def generate(self, metrics=None):
        pass


class SetGroup(WeightMixin, EmbeddedDocument):
    """
    A group of sets within a template.

    This might be all the sets for a given exercise, or some other
    grouping of sets like super-sets or a circuit.
    """
    name = StringField()
    children = ListField(GenericEmbeddedDocumentField())
    autogen = BooleanField()
    bottom = FloatField()
    top = FloatField()
    increment = FloatField()
    sets = IntField()
    reps = IntField()
    weight_expr = StringField()
    exercise = ReferenceField(Exercise)

    def find_exercise(self):
        node = self
        while node:
            if hasattr(node, 'exercise') and node.exercise:
                return node.exercise
            node = node._instance
        return None

    def generate(self, metrics=None):
        """
        Generate the sets from the set group's autogen configuration.
        """
        self.metric_group = metrics[self.find_exercise()]
        if self.autogen:
            self.children = []
            if self.sets and self.weight_expr:
                self.children = [Set(reps=self.reps, weight=self.weight_expr)] * self.sets
            elif self.bottom and self.top and self.increment:
                w = float(WeightExpr(self.bottom, metric_group=self.metric_group))
                inc = float(WeightExpr(self.increment, metric_group=self.metric_group))
                t = float(WeightExpr(self.top, metric_group=self.metric_group))
                while w <= t:
                    self.children.append(Set(reps=self.reps, weight=w))
                    w += inc
        else:
            for child in self.children:
                child.generate(metrics)


class Workout(EmbeddedDocument):
    """
    A workout template.
    """
    name = StringField()
    children = ListField(EmbeddedDocumentField(SetGroup))

    def generate(self, metrics=None):
        for c in self.children:
            c.generate(metrics=metrics)


class Block(EmbeddedDocument):
    """
    A program block.
    """
    name = StringField()
    inherit = StringField()
    variables = DictField()
    children = ListField(GenericEmbeddedDocumentField())

    def generate(self, metrics=None):
        for c in self.children:
            c.generate(metrics=metrics)


class Program(Document):
    """
    A program template. A program is a top-level grouping of Blocks or Workouts.
    A very simple program with no progression might contain workouts directly
    like this:

    program:
        name:   basic bodybuilding split
        children:
            - type: workout
              name: leg day
              children:
                - type: set_group
                  exercise: bodyweight squat
                  sets:
                    - reps: 10
                    - reps: 10
                    - reps: 10
                - type: set_group
                  exercise: leg press
                  sets:
                    - reps: 10
                    - reps: 10
                    - reps: 10

    More complicated programs can be defined by using arbitrary levels of
    nesting of blocks. For example, a multi-week program:

    program:
        name:   basic bodybuilding split
        children:
            - type: block
              name: week 1
              children:
              -  name: leg day
                 children:
                   - type: set_group
                     exercise: bodyweight squat
                     sets:
                       - reps: 10
                       - reps: 10
                       - reps: 10
                   - type: set_group
                     exercise: leg press
                     sets:
                       - reps: 10
                       - reps: 10
                       - reps: 10
            - type: block
              name: week 2
              children:
              -  name: leg day
                 children:
                   - type: set_group
                     exercise: bodyweight squat
                     sets:
                       - reps: 15
                       - reps: 15
                       - reps: 15
                   - type: set_group
                     exercise: leg press
                     sets:
                       - reps: 15
                       - reps: 15
                       - reps: 15

    Much more complex programs can be defined using nested blocks, where
    different levels of blocks represent macro/meso/microcycles/months/weeks.
    For example:

    program:
        mesocycle 1:
            month 1:
                week 1:
                    workout 1
                    workout 2
                    workout 3
            month 2:
                week 2
            ...
        mesocycle 2:
            ...
        mesocycle 3:
            ...
    """
    name = StringField()
    variables = DictField()
    metrics = EmbeddedDocumentField(MetricSet)
    children = ListField(GenericEmbeddedDocumentField())

    def generate(self):
        for c in self.children:
            c.generate(metrics=self.metrics)


def print_program(p, indent=0):
    """
    Print a textual representation of a program.
    """
    if hasattr(p, 'name') and p.name:
        print p.name
    for c in p.children:
        if isinstance(c, SetGroup) and c.exercise:
            print c.exercise.name
        if isinstance(c, Set):
            print "{}x{}kg".format(c.reps, c.weight)
        else:
            print_program(c)
