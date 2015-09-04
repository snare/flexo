from .metric import *
from .template import *
from .user import *
from .app import create_app


def main():
    global app
    app = create_app()
    app.run(debug=True)
