import json
from flask import Flask, jsonify, request, Blueprint, send_from_directory, current_app
from flask_restful import Resource, Api
from flask.ext.login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask.ext.mongoengine import MongoEngine
from passlib.hash import pbkdf2_sha256
from scruffy import *

from .metric import MetricGroup
from .user import User
from .program import Exercise

main = Blueprint('main', __name__)
login_manager = LoginManager()


def create_app(config_dict={}):
    global env, config

    # Set up scruffy environment
    env = Environment(
        dir=Directory('~/.flexo', create=False,
            config=ConfigFile('config', defaults=File('default.conf', parent=PackageDirectory()), apply_env=True)
        )
    )
    config = env.config

    # Setup flask app
    app = Flask(__name__, static_url_path='/static')
    app.secret_key = config.secret
    app.config["MONGODB_SETTINGS"] = {'host': config.db_uri}
    app.config.update(config_dict)
    app.register_blueprint(main)

    # Setup database
    app.db = MongoEngine(app)

    # Setup login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Setup API
    api = Api(app)
    api.add_resource(MetricAPI, '/api/metric')
    api.add_resource(ExerciseAPI, '/api/exercise')

    # Make sure there's at least an admin user
    if len(User.objects) == 0:
        User(name='admin', password='admin').save()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.objects(name=user_id)[0]


@main.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and current_user.is_authenticated:
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


@main.route('/api/logout')
def logout():
    logout_user()
    return jsonify({'ok': True, 'info': 'Logged out'})


@main.route('/')
def index():
    return current_app.send_static_file('index.html')


class MetricAPI(Resource):
    def get(self):
        return json.loads(MetricGroup.objects(user=current_user.id).to_json())


class ExerciseAPI(Resource):
    def get(self):
        return json.loads(Exercise.objects.to_json())
