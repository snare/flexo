from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask.ext.login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from mongoengine import *
from passlib.hash import pbkdf2_sha256
from scruffy import *


app = Flask(__name__, static_url_path='/static')
app.secret_key = 'baloney'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def setup():
    global env, config

    # Set up scruffy environment
    env = Environment(
        dir=Directory('~/.flexo', create=False,
            config=ConfigFile('config', defaults=File('default.conf', parent=PackageDirectory()), apply_env=True)
        )
    )
    config = env.config

    # Connect to the database
    connect(host=config.db_uri)

    # Make sure there's at least an admin user
    if len(User.objects) == 0:
        User(name='admin', password='admin').save()


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


@login_manager.user_loader
def load_user(user_id):
    return User.objects(name=user_id)[0]


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and current_user.is_authenticated():
        d = {'ok': True, 'name': current_user.name, 'info': 'Already authenticated'}
    else:
        try:
            data = request.get_json()
            users = User.objects(name=data['name'])
            if len(users) and pbkdf2_sha256.verify(data['password'], users[0].password_hash):
                login_user(users[0])
                d = {'ok': True, 'name': users[0].name, 'info': 'Successful authentication'}
            else:
                d = {'ok': False, 'info': 'Authentication failed'}
        except Exception as e:
            d = {'ok': False, 'info': 'Missing creds'}
    return jsonify(d)


@app.route('/logout')
def logout():
    logout_user()
    return jsonify({'ok': True, 'info': 'Logged out'})


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


setup()

api.add_resource(HelloWorld, '/')
