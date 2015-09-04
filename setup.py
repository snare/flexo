from setuptools import setup, find_packages

setup(
    name="flexo",
    version="0.1",
    author="snare",
    author_email="snare@ho.ax",
    description=(""),
    license="Buy snare a beer",
    keywords="",
    url="https://github.com/snare/flexo",
    packages=find_packages(),
    install_requires=['scruffington', 'mongoengine', 'flask', 'flask-restful', 'flask-login', 'flask-mongoengine',
                      'passlib'],
    entry_points={
        'console_scripts': ['flexo=flexo:main']
    }
)
