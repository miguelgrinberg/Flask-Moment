import pytest
from flask import Flask
from jinja2 import Template
from flask_moment import Moment

@pytest.fixture(scope='module')
def app():
    _app = Flask(__name__)
    with _app.app_context():
        yield _app

@pytest.fixture(scope='module')
def moment(app):
    moment = Moment()
    moment.init_app(app)
    yield moment