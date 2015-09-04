from mongoengine import *
from passlib.hash import pbkdf2_sha256
from flask.ext.login import UserMixin


class User(Document, UserMixin):
    """
    A user in the database.
    """
    name = StringField()
    password_hash = StringField()

    def __init__(self, password=None, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.password = password

    def __str__(self):
        return "User(name={})".format(self.name)

    def get_id(self):
        return self.name

    def save(self, *args, **kwargs):
        # Before we save, update the hash if there's a plaintext password present
        if self.password:
            self.password_hash = pbkdf2_sha256.encrypt(self.password, rounds=200000, salt_size=16)
            self.password = None
        super(User, self).save(*args, **kwargs)
