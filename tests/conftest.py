import pytest
from flask import Flask
from flask_moment import Moment
import datetime


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


@pytest.fixture(scope='module')
def current_time():
    return datetime.datetime(2017, 3, 10, 1, 49, 59, 38650)
