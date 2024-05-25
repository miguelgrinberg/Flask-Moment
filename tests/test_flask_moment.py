from datetime import datetime
import unittest
from unittest import mock

from flask import Flask, render_template_string
from markupsafe import Markup

from flask_moment import Moment, default_moment_version, default_moment_sri


class TestMoment(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.moment_app = Moment(self.app)
        self.appctx = self.app.app_context()
        self.moment = self.app.extensions['moment']
        self.appctx.push()

    def tearDown(self):
        self.appctx.pop()

    def test_init(self):
        assert self.app.extensions['moment'].__name__ == 'moment'
        assert self.app.template_context_processors[None][1].__globals__[
            '__name__'] == 'flask_moment'

    def test_init_app(self):
        app = Flask(__name__)
        moment = Moment()
        moment.init_app(app)
        assert app.extensions['moment'].__name__ == 'moment'
        assert app.template_context_processors[None][1].__globals__[
                   '__name__'] == 'flask_moment'

    def test_include_moment_directly(self):
        include_moment = self.moment.include_moment()
        assert isinstance(include_moment, Markup)
        assert '<script' in str(include_moment)
        assert default_moment_version + '/moment-with-locales.min.js' in str(
            include_moment)

    def test_include_moment_with_different_version_directly(self):
        include_moment = self.moment.include_moment(version='2.17.1')
        assert isinstance(include_moment, Markup)
        assert '<script' in str(include_moment)
        assert '2.17.1/moment-with-locales.min.js' in str(include_moment)

    def test_include_moment_with_local_js_directly(self):
        include_moment = self.moment.include_moment(
            local_js='/path/to/local/moment.js')
        assert isinstance(include_moment, Markup)
        assert '<script src="/path/to/local/moment.js"></script>' in str(
            include_moment)

    def test_include_moment_renders_properly(self):
        ts = str(render_template_string('{{ moment.include_moment() }}'))
        assert '<script' in ts
        assert default_moment_version + '/moment-with-locales.min.js' in ts
        assert 'moment.defaultFormat' not in ts

    def test_include_moment_with_default(self):
        self.app.config['MOMENT_DEFAULT_FORMAT'] = 'foo'
        ts = str(render_template_string('{{ moment.include_moment() }}'))
        assert '<script' in ts
        assert default_moment_version + '/moment-with-locales.min.js' in ts
        assert 'moment.defaultFormat = "foo";' in ts

    @mock.patch('flask_moment._naive_now')
    def test_moment_default(self, now):
        now.return_value = 'foo'
        m = self.moment()
        assert m.timestamp == 'foo'
        assert m.local is False

    @mock.patch('flask_moment._naive_now')
    def test_moment_local_true(self, now):
        now.return_value = 'foo'
        m = self.moment(local=True)
        assert m.timestamp == 'foo'
        assert m.local is True

    def test_locale(self):
        m = self.moment()
        locale = m.locale('en')
        assert isinstance(locale, Markup)
        assert 'moment.locale("en")' in str(locale)

    def test_lang(self):
        m = self.moment()
        lang = m.lang('en')
        assert isinstance(lang, Markup)
        assert 'moment.locale("en")' in str(lang)

    def test_flask_moment_js(self):
        js = self.moment_app.flask_moment_js()
        assert isinstance(js, str)
        assert 'function flask_moment_render(elem) {' in js

    def test__moment_datetime_passed(self):
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        m = self.moment(timestamp=ts)
        assert m.timestamp == ts
        assert m.local is False

    def test__moment_iso8601_passed(self):
        ts = '2017-01-15T22:47:06.479898Z'
        m = self.moment(timestamp=ts)
        assert m.timestamp == ts
        assert m.local is False

    @mock.patch('flask_moment._naive_now')
    def test__timestamp_as_iso_8601_default(self, now):
        now.return_value = datetime(2017, 1, 15, 22, 1, 21, 101361)
        m = self.moment()
        ts = m._timestamp_as_iso_8601(timestamp=m.timestamp)
        assert ts == '2017-01-15T22:01:21Z'

    @mock.patch('flask_moment._naive_now')
    def test__timestamp_as_iso_8601_local_true(self, now):
        now.return_value = datetime(2017, 1, 15, 22, 1, 21, 101361)
        m = self.moment(local=True)
        ts = m._timestamp_as_iso_8601(timestamp=m.timestamp)
        assert ts == '2017-01-15T22:01:21'

    def test__timestamp_as_iso_8601_string(self):
        ts = '2017-01-15T22:47:06.479898Z'
        m = self.moment(local=True)  # local is ignored in this case
        assert m._timestamp_as_iso_8601(timestamp=ts) == ts

    def test__render_default(self):
        m = self.moment()
        rts = m._render(func='format')  # rts: rendered time stamp
        assert isinstance(rts, Markup)
        assert rts.find('data-timestamp="') > 0
        assert rts.find('data-function="format" data-refresh="0"') > 0

    def test__render_refresh(self):
        m = self.moment()
        rts = m._render(func='format', refresh=True)
        assert isinstance(rts, Markup)
        assert rts.find('data-timestamp="') > 0
        assert rts.find('data-function="format" data-refresh="60000"') > 0

    def test_format_default(self):
        m = self.moment()
        rts = m.format('this-format-please')
        assert rts.find(
            'data-format="this-format-please" data-refresh="0"') > 0

    def test_fromNow_default(self):
        m = self.moment()
        rts = m.fromNow()
        assert rts.find('data-function="fromNow" data-refresh="0"') > 0

    def test_fromNow_no_suffix(self):
        m = self.moment()
        rts = m.fromNow(no_suffix=True)
        assert rts.find('data-function="fromNow" data-nosuffix="1" '
                        'data-refresh="0"') > 0

    def test_fromTime_default(self):
        m = self.moment()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        rts = m.fromTime(timestamp=ts)
        assert rts.find('data-function="from" data-timestamp2="{}" '
                        'data-refresh="0"'.format(
                            m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    def test_fromTime_no_suffix(self):
        m = self.moment()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        rts = m.fromTime(timestamp=ts, no_suffix=True)
        assert rts.find('data-function="from" data-timestamp2="{}" '
                        'data-nosuffix="1" data-refresh="0"'.format(
                            m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    def test_toNow_default(self):
        m = self.moment()
        rts = m.toNow()
        assert rts.find('data-function="toNow" data-refresh="0"') > 0

    def test_toNow_no_suffix(self):
        m = self.moment()
        no_suffix = True
        rts = m.toNow(no_suffix=no_suffix)
        assert rts.find('data-function="toNow" data-nosuffix="1" '
                        'data-refresh="0"') > 0

    def test_toTime_default(self):
        m = self.moment()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        rts = m.toTime(timestamp=ts)
        assert rts.find('data-function="to" data-timestamp2="{}" '
                        'data-refresh="0"'.format(
                            m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    def test_toTime_no_suffix(self):
        m = self.moment()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        no_suffix = True
        rts = m.toTime(timestamp=ts, no_suffix=no_suffix)
        assert rts.find('data-function="to" data-timestamp2="{}" '
                        'data-nosuffix="1" data-refresh="0"'.format(
                            m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    def test_calendar_default(self):
        m = self.moment()
        rts = m.calendar()
        assert rts.find('data-function="calendar" data-refresh="0"') > 0

    def test_valueOf_default(self):
        m = self.moment()
        rts = m.valueOf()
        assert rts.find('data-function="valueOf" data-refresh="0"') > 0

    def test_unix_default(self):
        m = self.moment()
        rts = m.unix()
        assert rts.find('data-function="unix" data-refresh="0"') > 0

    def test_diff_days(self):
        m = self.moment()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        rts = m.diff(ts, 'days')
        assert rts.find(
            'data-function="diff" data-timestamp2="{}" data-units="days" '
            'data-refresh="0"'.format(
                m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    def test_diff_hours(self):
        m = self.moment()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        rts = m.diff(ts, 'hours')
        assert rts.find(
            'data-function="diff" data-timestamp2="{}" data-units="hours" '
            'data-refresh="0"'.format(
                m._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(m._timestamp_as_iso_8601(
            timestamp=m.timestamp)) > 0

    @mock.patch('flask_moment._naive_now')
    def test_create_default_no_timestamp(self, now):
        ts = datetime(2017, 1, 15, 22, 1, 21, 101361)
        now.return_value = ts
        moment = Moment()
        moment.init_app(self.app)
        assert moment.create().timestamp == ts

    def test_create_default_with_timestamp(self):
        moment = Moment()
        moment.init_app(self.app)
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        assert moment.create(timestamp=ts).timestamp == ts

    def test_moment_with_non_default_versions(self):
        include_moment = None

        def _check_assertions():
            assert 'src=\"' in include_moment
            assert 'integrity=\"' not in include_moment
            assert 'crossorigin\"' not in include_moment

        include_moment = self.moment.include_moment(version='2.8.0')
        _check_assertions()
        include_moment = self.moment.include_moment(version='2.3.1')
        _check_assertions()
        include_moment = self.moment.include_moment(version='2.16.8')
        _check_assertions()
        include_moment = self.moment.include_moment(version='2.30.1')
        _check_assertions()

    def test_moment_with_default_version(self):
        include_moment = self.moment.include_moment()
        assert include_moment.startswith(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/{}'
            '/moment-with-locales.min.js" integrity="{}" '
            'crossorigin="anonymous"></script>'.format(
                default_moment_version, default_moment_sri))

    def test_moment_from_cdn_with_custom_sri_hash(self):
        include_moment = self.moment.include_moment(sri='sha384-12345678')
        assert include_moment.startswith(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/{}'
            '/moment-with-locales.min.js" integrity="sha384-12345678" '
            'crossorigin="anonymous"></script>'.format(default_moment_version))

        include_moment = self.moment.include_moment(version='2.0.0',
                                                    sri='sha384-12345678')
        assert include_moment.startswith(
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/'
            '2.0.0/moment-with-langs.min.js" integrity="sha384-12345678" '
            'crossorigin="anonymous"></script>')

    def test_moment_local(self):
        include_moment = self.moment.include_moment(local_js=True)
        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin\"' not in include_moment

    def test_moment_local_with_sri(self):
        include_moment = self.moment.include_moment(local_js=True,
                                                    sri='sha384-87654321')
        assert 'src=\"' in include_moment
        assert 'integrity=\"sha384-87654321\"' in include_moment
        assert 'crossorigin=\"anonymous\"' in include_moment

    def test_disabling_moment_default(self):
        include_moment = self.moment.include_moment(sri=False)
        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment

    def test_disabling_moment_custom(self):
        include_moment = self.moment.include_moment(local_js=True, sri=False)
        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment

    def test_disabling_moment_custom_version(self):
        include_moment = self.moment.include_moment(version='2.17.9',
                                                    sri=False)
        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment
