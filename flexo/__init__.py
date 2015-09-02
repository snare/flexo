from .metric import *
from .template import *
from .app import setup, app, User


def main():
    setup()
    app.run(debug=True)
