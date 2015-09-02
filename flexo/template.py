from mongoengine import *

from .user import User


class Exercise(Document):
    """
    An exercise.
    """
    name = StringField()
    meta = {'allow_inheritance': True}


class StrengthExercise(Exercise):
    """
    A strength training exercise, e.g. Squat.
    """


class Expression(EmbeddedDocument):
    """
    An expression used for dynamic calculations of weight etc.
    """


class TemplateSet(EmbeddedDocument):
    """
    A set of an exercise.
    """
    kind = IntField()
    reps = IntField()
    weight = EmbeddedDocumentField(Expression)
    rpe = FloatField()
    duration = DateTimeField()
    distance = FloatField()


class TemplateSetGroup(EmbeddedDocument):
    """
    A group of sets within a template.

    This might be all the sets for a given exercise, or some other
    grouping of sets like super-sets or a circuit.
    """
    sets = ListField(EmbeddedDocumentField(TemplateSet))


class Template(Document):
    """
    A workout template.
    """
    user = ReferenceField(User)
    groups = ListField(EmbeddedDocumentField(TemplateSetGroup))
