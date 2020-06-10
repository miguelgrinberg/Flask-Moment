from datetime import datetime
from flask import render_template_string
from jinja2 import Markup
from flask_moment import _moment, Moment, default_jquery_version, \
    default_moment_version, default_moment_sri


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
        assert '<script' in str(include_moment)
        assert default_moment_version + '/moment-with-locales.min.js' in str(
            include_moment)

    def test_include_moment_with_different_version_directly(self):
        include_moment = _moment.include_moment(version='2.17.1')

        assert isinstance(include_moment, Markup)
        assert '<script' in str(include_moment)
        assert '2.17.1/moment-with-locales.min.js' in str(include_moment)

    def test_include_moment_with_local_js_directly(self):
        include_moment = _moment.include_moment(
            local_js='/path/to/local/moment.js')

        assert isinstance(include_moment, Markup)
        assert '<script src="/path/to/local/moment.js"></script>' in str(
            include_moment)

    def test_include_moment_renders_properly(self, app, moment):
        ts = str(render_template_string('{{ moment.include_moment() }}'))

        assert '<script' in ts
        assert default_moment_version + '/moment-with-locales.min.js' in ts
        assert 'moment.defaultFormat' not in ts

    def test_include_moment_with_default(self, app, moment):
        app.config['MOMENT_DEFAULT_FORMAT'] = 'foo'
        ts = str(render_template_string('{{ moment.include_moment() }}'))
        assert '<script' in ts
        assert default_moment_version + '/moment-with-locales.min.js' in ts
        assert 'moment.defaultFormat = "foo";' in ts

    def test_include_jquery_default(self):
        include_jquery = _moment.include_jquery()

        assert isinstance(include_jquery, Markup)
        assert all([each in str(include_jquery) for each in [
            'code.jquery.com', default_jquery_version]])

    def test_include_jquery_local(self):
        include_jquery = _moment.include_jquery(local_js=True)

        assert all([each in str(include_jquery) for each in [
            '<script', '</script>']])


class TestPrivateMomentClass(object):
    """Tests for the _moment class"""

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
        locale = mom.locale('en')
        assert isinstance(locale, Markup)
        assert 'moment.locale("en")' in str(locale)

    def test_lang(self):
        mom = _moment_mock()
        lang = mom.lang('en')
        assert isinstance(lang, Markup)
        assert 'moment.locale("en")' in str(lang)

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
        rts = mom._render(func='format')  # rts: rendered time stamp

        assert isinstance(rts, Markup)
        assert rts.find('data-timestamp="') > 0
        assert rts.find('data-function="format" data-refresh="0"') > 0

    def test__render_refresh(self):
        mom = _moment_mock()
        rts = mom._render(func='format', refresh=True)

        assert isinstance(rts, Markup)
        assert rts.find('data-timestamp="') > 0
        assert rts.find('data-function="format" data-refresh="60000"') > 0

    def test_format_default(self):
        mom = _moment_mock()
        rts = mom.format('this-format-please')

        assert rts.find(
            'data-format="this-format-please" data-refresh="0"') > 0

    def test_fromNow_default(self):
        mom = _moment_mock()
        rts = mom.fromNow()

        assert rts.find('data-function="fromNow" data-refresh="0"') > 0

    def test_fromNow_no_suffix(self):
        mom = _moment_mock()
        rts = mom.fromNow(no_suffix=True)

        assert rts.find('data-function="fromNow" data-nosuffix="1" '
                        'data-refresh="0"') > 0

    def test_fromTime_default(self):
        mom = _moment_mock()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        rts = mom.fromTime(timestamp=ts)

        assert rts.find('data-function="from" data-timestamp2="{}" '
                        'data-refresh="0"'.format(
                            mom._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_fromTime_no_suffix(self):
        mom = _moment_mock()
        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)
        rts = mom.fromTime(timestamp=ts, no_suffix=True)

        assert rts.find('data-function="from" data-timestamp2="{}" '
                        'data-nosuffix="1" data-refresh="0"'.format(
                            mom._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_toNow_default(self):
        mom = _moment_mock()
        rts = mom.toNow()

        assert rts.find('data-function="toNow" data-refresh="0"') > 0

    def test_toNow_no_suffix(self):
        mom = _moment_mock()
        no_suffix = True
        rts = mom.toNow(no_suffix=no_suffix)

        assert rts.find('data-function="toNow" data-nosuffix="1" '
                        'data-refresh="0"') > 0

    def test_toTime_default(self):
        mom = _moment_mock()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        rts = mom.toTime(timestamp=ts)

        assert rts.find('data-function="to" data-timestamp2="{}" '
                        'data-refresh="0"'.format(
                            mom._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_toTime_no_suffix(self):
        mom = _moment_mock()
        ts = datetime(2020, 1, 15, 22, 47, 6, 479898)
        no_suffix = True
        rts = mom.toTime(timestamp=ts, no_suffix=no_suffix)

        assert rts.find('data-function="to" data-timestamp2="{}" '
                        'data-nosuffix="1" data-refresh="0"'.format(
                            mom._timestamp_as_iso_8601(ts))) > 0
        assert rts.find(mom._timestamp_as_iso_8601(
            timestamp=mom.timestamp)) > 0

    def test_calendar_default(self):
        mom = _moment_mock()
        rts = mom.calendar()

        assert rts.find('data-function="calendar" data-refresh="0"') > 0

    def test_valueOf_default(self):
        mom = _moment_mock()
        rts = mom.valueOf()

        assert rts.find('data-function="valueOf" data-refresh="0"') > 0

    def test_unix_default(self):
        mom = _moment_mock()
        rts = mom.unix()

        assert rts.find('data-function="unix" data-refresh="0"') > 0


class TestPublicMomentClass(object):
    """Tests for the Moment class"""

    def test_create_default_no_timestamp(self, app):
        moment = _Moment()
        moment.init_app(app)

        assert moment.create().timestamp == _datetime_mock.utcnow()

    def test_create_default_with_timestamp(self, app):
        moment = _Moment()
        moment.init_app(app)

        ts = datetime(2017, 1, 15, 22, 47, 6, 479898)

        assert moment.create(timestamp=ts).timestamp == ts


class TestSubresourceIntegrity(object):
    def test_jquery_with_non_default_version(self):
        include_jquery = _moment.include_jquery(version='2.0.9')

        assert 'src=\"' in include_jquery
        assert 'integrity=\"' not in include_jquery
        assert 'crossorigin=\"' not in include_jquery

    def test_jquery_with_default_version(self):
        include_jquery = _moment.include_jquery()

        assert 'src=\"' in include_jquery
        assert 'integrity=\"sha' in include_jquery
        assert 'crossorigin=\"anonymous\"' in include_jquery

    def test_jquery_from_cdn_without_custom_sri_hash(self):
        include_jquery = _moment.include_jquery(version='2.1.1',
                                                sri='sha384-12345678')

        assert ('<script src=\"//code.jquery.com/jquery-2.1.1.min.js\"'
                ' integrity=\"sha384-12345678\" crossorigin=\"anonymous\">'
                '</script>') == include_jquery

    def test_jquery_local_has_no_sri_as_default(self):
        include_jquery = _moment.include_jquery(local_js=True)

        assert 'src=\"' in include_jquery
        assert 'integrity=\"' not in include_jquery
        assert 'crossorigin\"' not in include_jquery

    def test_jquery_local_with_sri(self):
        include_jquery = _moment.include_jquery(local_js=True,
                                                sri='sha384-12345678')

        assert ('<script src=\"True\" integrity=\"sha384-12345678\"'
                ' crossorigin=\"anonymous\"></script>\n') == include_jquery

    def test_disabling_sri_jquery_default(self):
        include_jquery = _moment.include_jquery(sri=False)

        assert 'src=\"' in include_jquery
        assert 'integrity=\"' not in include_jquery
        assert 'crossorigin\"' not in include_jquery

    def test_disabling_sri_jquery_custom_js(self):
        include_jquery = _moment.include_jquery(local_js=True, sri=False)

        assert 'src=\"' in include_jquery
        assert 'integrity=\"' not in include_jquery
        assert 'crossorigin\"' not in include_jquery

    def test_disabling_sri_jquery_custom_version(self):
        include_jquery = _moment.include_jquery(version='2.1.1', sri=False)

        assert 'src=\"' in include_jquery
        assert 'integrity=\"' not in include_jquery
        assert 'crossorigin\"' not in include_jquery

    def test_moment_with_non_default_versions(self):
        include_moment = None

        def _check_assertions():
            assert 'src=\"' in include_moment
            assert 'integrity=\"' not in include_moment
            assert 'crossorigin\"' not in include_moment

        include_moment = _moment.include_moment(version='2.8.0')
        _check_assertions()
        include_moment = _moment.include_moment(version='2.3.1')
        _check_assertions()
        include_moment = _moment.include_moment(version='2.16.8')
        _check_assertions()
        include_moment = _moment.include_moment(version='2.30.1')
        _check_assertions()

    def test_moment_with_default_version(self):
        include_moment = _moment.include_moment()

        assert include_moment.startswith(
            '<script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/{}'
            '/moment-with-locales.min.js" integrity="{}" '
            'crossorigin="anonymous"></script>'.format(
                default_moment_version, default_moment_sri))

    def test_moment_from_cdn_with_custom_sri_hash(self):
        include_moment = _moment.include_moment(sri='sha384-12345678')

        assert include_moment.startswith(
            '<script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/{}'
            '/moment-with-locales.min.js" integrity="sha384-12345678" '
            'crossorigin="anonymous"></script>'.format(default_moment_version))

        include_moment = _moment.include_moment(version='2.0.0',
                                                sri='sha384-12345678')

        assert include_moment.startswith(
            '<script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/2.0.0'
            '/moment-with-langs.min.js" integrity="sha384-12345678" '
            'crossorigin="anonymous"></script>')

    def test_moment_local(self):
        include_moment = _moment.include_moment(local_js=True)

        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin\"' not in include_moment

    def test_moment_local_with_sri(self):
        include_moment = _moment.include_moment(local_js=True,
                                                sri='sha384-87654321')

        assert 'src=\"' in include_moment
        assert 'integrity=\"sha384-87654321\"' in include_moment
        assert 'crossorigin=\"anonymous\"' in include_moment

    def test_disabling_moment_default(self):
        include_moment = _moment.include_moment(sri=False)

        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment

    def test_disabling_moment_custom(self):
        include_moment = _moment.include_moment(local_js=True, sri=False)

        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment

    def test_disabling_moment_custom_version(self):
        include_moment = _moment.include_moment(version='2.17.9', sri=False)

        assert 'src=\"' in include_moment
        assert 'integrity=\"' not in include_moment
        assert 'crossorigin' not in include_moment
