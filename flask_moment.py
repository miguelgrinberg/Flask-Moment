import json
from distutils.version import StrictVersion
from datetime import datetime
from markupsafe import Markup
from flask import current_app

# //code.jquery.com/jquery-3.5.1.min.js
default_jquery_version = '3.5.1'
default_jquery_sri = ('sha384-ZvpUoO/+PpLXR1lu4jmpXWu80pZlYUAfxl5NsBMWOEPSjUn'
                      '/6Z/hRTt8+pR6L4N2')

# //cdnjs.cloudflare.com/ajax/libs/moment.js/2.27.0/moment-with-locales.min.js
default_moment_version = '2.29.1'
default_moment_sri = ('sha512-LGXaggshOkD/at6PFNcp2V2unf9LzFq6LE+sChH7ceMTDP0'
                      'g2kn6Vxwgg7wkPP7AAtX+lmPqPdxB47A0Nz0cMQ==')


class _moment(object):
    FUNCTION_DATA_KEY = 'function'
    TIMESTAMP_DATA_KEY = 'timestamp'
    PARAMS_DATA_KEY = 'params'
    FORMAT_DATA_KEY = 'format'
    REFRESH_DATA_KEY = 'refresh'

    @classmethod
    def include_moment(cls, version=default_moment_version, local_js=None,
                       no_js=None, sri=None, with_locales=True):
        js = ''
        if version == default_moment_version and local_js is None and \
                sri is None:
            sri = default_moment_sri
        if not no_js:
            if local_js is not None:
                if not sri:
                    js = '<script src="{}"></script>\n'.format(local_js)
                else:
                    js = ('<script src="{}" integrity="{}" '
                          'crossorigin="anonymous"></script>\n').format(
                              local_js, sri)
            elif version is not None:
                if with_locales:
                    js_filename = 'moment-with-locales.min.js' \
                        if StrictVersion(version) >= StrictVersion('2.8.0') \
                        else 'moment-with-langs.min.js'
                else:
                    js_filename = 'moment.min.js'

                if not sri:
                    js = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/'
                          'moment.js/{}/{}"></script>\n').format(
                              version, js_filename)
                else:
                    js = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/'
                          'moment.js/{}/{}" integrity="{}" '
                          'crossorigin="anonymous"></script>\n').format(
                              version, js_filename, sri)

        default_format = ''
        if 'MOMENT_DEFAULT_FORMAT' in current_app.config:
            default_format = '\nmoment.defaultFormat = "{}";'.format(
                current_app.config['MOMENT_DEFAULT_FORMAT'])
        return Markup('''{js}<script>
moment.locale("en");{default_format}
function flask_moment_render(elem) {{
    timestamp = moment($(elem).data('{timestamp_data_key}'));
    func = $(elem).data('{function_data_key}');
    params = $(elem).data('{params_data_key}');
    format = $(elem).data('{format_data_key}');
    func_res = timestamp[func].apply(timestamp, params)
    // we can't use moment js chaining like moment().add(1, 'days').format('L')
    // because of one-way communication between python and js code
    // so we must pass format as parameter to functions that return raw datetime
    // to pretty print result in templates
    if (func !== 'format' && format)
        func_res = func_res.format(format)
    $(elem).text(func_res);
    $(elem).removeClass('flask-moment').show();
}}
function flask_moment_render_all() {{
    $('.flask-moment').each(function() {{
        flask_moment_render(this);
        refresh = $(this).data('{refresh_data_key}')
        if (refresh) {{
            (function(elem, interval) {{ setInterval(function() {{ flask_moment_render(elem) }}, interval); }})(this, refresh);
        }}
    }})
}}
$(document).ready(function() {{
    flask_moment_render_all();
}});
</script>'''.format(
            js=js,
            default_format=default_format,
            timestamp_data_key=cls.TIMESTAMP_DATA_KEY,
            function_data_key=cls.FUNCTION_DATA_KEY,
            params_data_key=cls.PARAMS_DATA_KEY,
            format_data_key=cls.FORMAT_DATA_KEY,
            refresh_data_key=cls.REFRESH_DATA_KEY,
        ))  # noqa: E501

    @staticmethod
    def include_jquery(version=default_jquery_version, local_js=None,
                       sri=None):
        js = ''
        if sri is None and version == default_jquery_version and \
                local_js is None:
            sri = default_jquery_sri
        if local_js is not None:
            if not sri:
                js = '<script src="{}"></script>\n'.format(local_js)
            else:
                js = ('<script src="{}" integrity="{}" '
                      'crossorigin="anonymous"></script>\n').format(
                          local_js, sri)

        else:
            if not sri:
                js = ('<script src="https://code.jquery.com/' +
                      'jquery-{}.min.js"></script>').format(version)
            else:
                js = ('<script src="https://code.jquery.com/jquery-{}.min.js" '
                      'integrity="{}" crossorigin="anonymous">'
                      '</script>').format(version, sri)
        return Markup(js)

    @staticmethod
    def locale(language='en', auto_detect=False, customization=None):
        if auto_detect:
            return Markup('<script>\nvar locale = '
                          'window.navigator.userLanguage || '
                          'window.navigator.language;\n'
                          'moment.locale(locale);\n</script>')
        if customization:
            return Markup(
                '<script>\nmoment.locale("{}", {});\n</script>'.format(
                    language, customization))
        return Markup(
            '<script>\nmoment.locale("{}");\n</script>'.format(language))

    @staticmethod
    def lang(language):
        return _moment.locale(language)

    def __init__(self, timestamp=None, local=False):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp
        self.local = local

    def _timestamp_as_iso_8601(self, timestamp):
        tz = ''
        if not self.local:
            tz = 'Z'
        return timestamp.strftime('%Y-%m-%dT%H:%M:%S' + tz)

    def _serialize_js_params(self, params):
        serialized = []
        for param in params:
            if isinstance(param, datetime):
                serialized.append(self._timestamp_as_iso_8601(param))
            else:
                serialized.append(param)
        return json.dumps(serialized)

    def _render(self, func, *params, format=None, refresh=False):
        t = self._timestamp_as_iso_8601(self.timestamp)
        data_values = 'data-{}="{}"'.format(self.TIMESTAMP_DATA_KEY, t)
        data_values += ' data-{}="{}"'.format(self.FUNCTION_DATA_KEY, func)
        if format:
            data_values += ' data-{}="{}"'.format(self.FORMAT_DATA_KEY, format)
        if params:
            data_values += " data-{}='{}'".format(
                self.PARAMS_DATA_KEY,
                self._serialize_js_params(params),
            )
        data_values += ' data-{}="{}"'.format(
            self.REFRESH_DATA_KEY,
            int(refresh) * 60000
        )

        return Markup("""
            <span
                class="flask-moment"
                {}
                style="display: none"
            >{}</span>
        """.format(data_values, t))

    def format(self, format, refresh=False):
        return self._render("format", format, refresh=refresh)

    def fromNow(self, no_suffix=False, refresh=False):
        return self._render("fromNow", no_suffix, refresh=refresh)

    def fromTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("from", timestamp, no_suffix, refresh=refresh)

    def toNow(self, no_suffix=False, refresh=False):
        return self._render("toNow", no_suffix, refresh=refresh)

    def toTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("to", timestamp, no_suffix, refresh=refresh)

    def calendar(self, refresh=False):
        return self._render("calendar", refresh=refresh)

    def valueOf(self, refresh=False):
        return self._render("valueOf", refresh=refresh)

    def unix(self, refresh=False):
        return self._render("unix", refresh=refresh)

    def diff(self, timestamp, units=None, as_float=False, refresh=False):
        return self._render(
            "diff", timestamp, units, as_float, refresh=refresh
        )

    def add(self, value, units, as_float=False, format=None, refresh=False):
        return self._render(
            "add", value, units, as_float, format=format, refresh=refresh
        )

    def subtract(self, value, units, as_float=False, format=None, refresh=False):
        return self._render(
            "subtract", value, units, as_float, format=format, refresh=refresh
        )


class Moment(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['moment'] = _moment
        app.context_processor(self.context_processor)

    @staticmethod
    def context_processor():
        return {
            'moment': current_app.extensions['moment']
        }

    def create(self, timestamp=None):
        return current_app.extensions['moment'](timestamp)
