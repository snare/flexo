import program
from .app import create_app


def main():
    global app
    app = create_app()
    app.run(debug=True)
