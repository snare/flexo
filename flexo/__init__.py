from scruffy import *

from .metric import *
from .template import *
from .app import app, User


def main():
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

    # Run the app
    app.run(debug=True)
