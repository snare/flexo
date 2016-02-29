from mongoengine import *


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
