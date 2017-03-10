from datetime import datetime

from flask import render_template_string
from flask_moment import _moment, Moment
from jinja2 import Markup


# Mock Objects

class NewDate(datetime):
    """http://stackoverflow.com/questions/4481954"""
    @classmethod
    def utcnow(cls):
        return cls(2017, 1, 15, 22, 1, 21, 101361)


_datetime_mock = NewDate


class NewPrivateMoment(_moment):
    """Mock the _moment class for predictable now timestamps"""
    def __init__(self, timestamp=None, local=False):
        if timestamp is None:
            timestamp = _datetime_mock.utcnow()
        self.timestamp = timestamp
        self.local = local


_moment_mock = NewPrivateMoment


class NewPublicMoment(Moment):
    """Mock the Moment class for predictable now timestamps"""
    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['moment'] = _moment_mock
        app.context_processor(self.context_processor)


_Moment = NewPublicMoment


# Testing

class TestFlaskAppSetup(object):

    def test_init_app(self, app, moment):
        assert app.extensions['moment'] == _moment

    def test_app_context_processor(self, app, moment):
        assert app.template_context_processors[None][1].__globals__[
            '__name__'] == 'flask_moment'


class TestFlaskMomentIncludes(object):

    def test_include_moment_directly(self):
        include_moment = _moment.include_moment()

        assert isinstance(include_moment, Markup)
        assert "<script" in str(include_moment)
        assert "2.10.3/moment-with-locales.min.js" in str(include_moment)

    def test_include_moment_with_different_version_directly(self):
        include_moment = _moment.include_moment(version="2.17.1")

        assert isinstance(include_moment, Markup)
        assert "<script" in str(include_moment)
        assert "2.17.1/moment-with-locales.min.js" in str(include_moment)

    def test_include_moment_with_local_js_directly(self):
        include_moment = _moment.include_moment(
            local_js="/path/to/local/moment.js")

        assert isinstance(include_moment, Markup)
        assert "<script src=\"/path/to/local/moment.js\"></script>" in str(
            include_moment)

    def test_include_moment_renders_properly(self, app, moment):
        ts = str(render_template_string("{{ moment.include_moment() }}"))

        assert "<script" in ts
        assert "2.10.3/moment-with-locales.min.js" in str(ts)

    def test_include_jquery_default(self):
        include_jquery = _moment.include_jquery()

        assert isinstance(include_jquery, Markup)
        assert all([each in str(include_jquery) for each in [
            'code.jquery.com', '2.1.0']])

    def test_include_jquery_local(self):
        include_jquery = _moment.include_jquery(local_js=True)

        assert all([each in str(include_jquery) for each in [
            '<script', '</script>']])


class TestPrivateMomentClass(object):
    '''Private refers to the _moment class'''

    def test__moment_default(self):
        mom = _moment_mock()
        assert mom.timestamp == _datetime_mock.utcnow()
        assert mom.local is False

    def test__moment_local_true(self):
        mom = _moment_mock(local=True)
        assert mom.timestamp == _datetime_mock.utcnow()
        assert mom.local is True

    def test_locale(self):
        mom = _moment_mock()
        l = 'en'
        locale = mom.locale(l)
        assert isinstance(locale, Markup)
        assert 'moment.locale("%s")' % l in str(locale)

    def test_lang(self):
        mom = _moment_mock()
        l = 'en'
        lang = mom.lang(l)
        assert isinstance(lang, Markup)
        assert 'moment.locale("%s")' % l in str(lang)

    def test__moment_timestamp_passed(self):
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        mom = _moment_mock(timestamp=ts)
        assert mom.timestamp == ts
        assert mom.local is False

    def test__timestamp_as_iso_8601_default(self):
        mom = _moment_mock()
        ts = mom._timestamp_as_iso_8601(timestamp=mom.timestamp)
        assert ts == '2017-01-15T22:01:21Z'

    def test__timestamp_as_iso_8601_local_true(self):
        mom = _moment_mock(local=True)
        ts = mom._timestamp_as_iso_8601(timestamp=mom.timestamp)
        assert ts == '2017-01-15T22:01:21'

    def test__render_default(self):
        mom = _moment_mock()
        refresh = False
        rts = mom._render(format="format")  # rts: rendered time stamp

        assert isinstance(rts, Markup)
        assert rts.find("thisisnotinthemarkup") < 0
        assert rts.find("\"format\"") > 0
        assert rts.find("data-refresh=\""+str(int(refresh)*60000)+"\"") > 0

    def test__render_refresh(self):
        mom = _moment_mock()
        refresh = True
        rts = mom._render(format="format", refresh=refresh)

        assert isinstance(rts, Markup)
        assert not rts.find("thisisnotinthemarkup") > 0
        assert rts.find("\"format\"") > 0
        assert rts.find("data-refresh=\""+str(int(refresh)*60000)+"\"") > 0

    def test_format_default(self):
        mom = _moment_mock()
        rts = mom.format("this-format-please")

        assert rts.find("this-format-please") > 0

    def test_fromNow_default(self):
        mom = _moment_mock()
        no_suffix = False
        rts = mom.fromNow()

        assert rts.find("fromNow(%s)" % int(no_suffix)) > 0

    def test_fromNow_no_suffix(self):
        mom = _moment_mock()
        no_suffix = True
        rts = mom.fromNow(no_suffix=no_suffix)

        assert rts.find("fromNow(%s)" % int(no_suffix)) > 0

    def test_fromTime_default(self):
        mom = _moment_mock()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        no_suffix = False
        rts = mom.fromTime(timestamp=ts)

        assert rts.find("from(moment('%s'),%s)"
                        % (mom._timestamp_as_iso_8601(ts), int(no_suffix))) > 0
        assert rts.find("%s" % mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_fromTime_no_suffix(self):
        mom = _moment_mock()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        no_suffix = True
        rts = mom.fromTime(timestamp=ts, no_suffix=no_suffix)

        assert rts.find("from(moment('%s'),%s)"
                        % (mom._timestamp_as_iso_8601(ts), int(no_suffix))) > 0
        assert rts.find("%s" % mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_calendar_default(self):
        mom = _moment_mock()
        rts = mom.calendar()

        assert rts.find("data-format=\"calendar()\"") > 0

    def test_valueOf_default(self):
        mom = _moment_mock()
        rts = mom.valueOf()

        assert rts.find("data-format=\"valueOf()\"") > 0

    def test_unix_default(self):
        mom = _moment_mock()
        rts = mom.unix()

        assert rts.find("data-format=\"unix()\"") > 0


class TestPublicMomentClass(object):
    '''Public refers to the Moment class'''
    def test_create_default_no_timestamp(self, app):
        moment = _Moment()
        moment.init_app(app)

        assert moment.create().timestamp == _datetime_mock.utcnow()

    def test_create_default_with_timestamp(self, app):
        moment = _Moment()
        moment.init_app(app)

        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)

        assert moment.create(timestamp=ts).timestamp == ts
