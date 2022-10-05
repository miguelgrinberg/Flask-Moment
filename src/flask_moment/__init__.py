from datetime import datetime
from packaging.version import parse as version_parse
from markupsafe import Markup
from flask import current_app

# //cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment-with-locales.min.js
default_moment_version = '2.29.4'
default_moment_sri = ('sha512-42PE0rd+wZ2hNXftlM78BSehIGzezNeQuzihiBCvUEB3CVx'
                      'HvsShF86wBWwQORNxNINlBPuq7rG4WWhNiTVHFg==')

js_code = '''function flask_moment_render(elem) {{
    const timestamp = moment(elem.dataset.timestamp);
    const func = elem.dataset.function;
    const format = elem.dataset.format;
    const timestamp2 = elem.dataset.timestamp2;
    const no_suffix = elem.dataset.nosuffix;
    const units = elem.dataset.units;
    let args = [];
    if (format)
        args.push(format);
    if (timestamp2)
        args.push(moment(timestamp2));
    if (no_suffix)
        args.push(no_suffix);
    if (units)
        args.push(units);
    elem.textContent = timestamp[func].apply(timestamp, args);
    elem.classList.remove('flask-moment');
    elem.style.display = "";
}}
function flask_moment_render_all() {{
    const moments = document.querySelectorAll('.flask-moment');
    moments.forEach(function(moment) {{
        flask_moment_render(moment);
        const refresh = moment.dataset.refresh;
        if (refresh && refresh > 0) {{
            (function(elem, interval) {{
                setInterval(function() {{
                    flask_moment_render(elem);
                }}, interval);
            }})(moment, refresh);
        }}
    }})
}}
document.addEventListener("DOMContentLoaded", flask_moment_render_all);'''


class moment(object):
    """Create a moment object.

    :param timestamp: The ``datetime`` object representing the timestamp.
    :param local: If ``True``, the ``timestamp`` argument is given in the
                  local client time. In most cases this argument will be set
                  to ``False`` and all the timestamps managed by the server
                  will be in the UTC timezone.
    """
    @classmethod
    def include_moment(cls, version=default_moment_version, local_js=None,
                       no_js=None, sri=None, with_locales=True):
        """Include the moment.js library and the supporting JavaScript code
        used by this extension.

        This function must be called in the ``<head>`` section of the Jinja
        template(s) that use this extension.

        :param version: The version of moment.js to include.
        :param local_js: The URL to import the moment.js library from. Use this
                         option to import the library from a locally hosted
                         file.
        :param no_js: Just add the supporting code for this extension, without
                      importing the moment.js library. . Use this option if
                      the library is imported elsewhere in the template. The
                      supporting JavaScript code for this extension is still
                      included.
        :param sri: The SRI hash to use when importing the moment.js library,
                    or ``None`` if the SRI hash is unknown or disabled.
        :param with_locales: If ``True``, include the version of moment.js that
                             has all the locales.
        """
        mjs = ''
        if version == default_moment_version and local_js is None and \
                with_locales is True and sri is None:
            sri = default_moment_sri
        if not no_js:
            if local_js is not None:
                if not sri:
                    mjs = '<script src="{}"></script>\n'.format(local_js)
                else:
                    mjs = ('<script src="{}" integrity="{}" '
                           'crossorigin="anonymous"></script>\n').format(
                               local_js, sri)
            elif version is not None:
                if with_locales:
                    js_filename = 'moment-with-locales.min.js' \
                        if version_parse(version) >= version_parse('2.8.0') \
                        else 'moment-with-langs.min.js'
                else:
                    js_filename = 'moment.min.js'

                if not sri:
                    mjs = ('<script src="https://cdnjs.cloudflare.com/ajax/'
                           'libs/moment.js/{}/{}"></script>\n').format(
                               version, js_filename)
                else:
                    mjs = ('<script src="https://cdnjs.cloudflare.com/ajax/'
                           'libs/moment.js/{}/{}" integrity="{}" '
                           'crossorigin="anonymous"></script>\n').format(
                               version, js_filename, sri)
        return Markup('{}\n<script>\n{}\n</script>\n'''.format(
            mjs, cls.flask_moment_js()))

    @staticmethod
    def locale(language='en', auto_detect=False, customization=None):
        """Configure the moment.js locale.

        :param language: The language code.
        :param auto_detect: If ``True``, detect the locale from the browser.
        :param customization: A dictionary with custom options for the locale,
                              as needed by the moment.js library.
        """
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
    def flask_moment_js():
        """Return the JavaScript supporting code for this extension.

        This method is provided to enable custom configurations that are not
        supported by ``include_moment``. The return value of this method is
        a string with raw JavaScript code. This code can be added to your own
        ``<script>`` tag in a template file::

            <script>
                {{ moment.flask_moment_js() }}
            </script>

        Alternatively, the code can be returned in a JavaScript endpoint that
        can be loaded from the HTML file as an external resource::

            @app.route('/flask-moment.js')
            def flask_moment_js():
                return (moment.flask_moment_js(), 200,
                    {'Content-Type': 'application/javascript'})

        Note: only the code specific to Flask-Moment is included. When using
        this method, you must include the moment.js library separately.
        """
        default_format = ''
        if 'MOMENT_DEFAULT_FORMAT' in current_app.config:
            default_format = '\nmoment.defaultFormat = "{}";'.format(
                current_app.config['MOMENT_DEFAULT_FORMAT'])
        return '''moment.locale("en");{}\n{}'''.format(default_format, js_code)

    @staticmethod
    def lang(language):
        """Set the language. This is a simpler version of the :func:`locale`
        function.

        :param language: The language code to use.
        """
        return moment.locale(language)

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

    def _render(self, func, format=None, timestamp2=None, no_suffix=None,
                units=None, refresh=False):
        t = self._timestamp_as_iso_8601(self.timestamp)
        data_values = 'data-function="{}"'.format(func)
        if format:
            data_values += ' data-format="{}"'.format(format)
        if timestamp2:
            data_values += ' data-timestamp2="{}"'.format(timestamp2)
        if no_suffix:
            data_values += ' data-nosuffix="1"'
        if units:
            data_values += ' data-units="{}"'.format(units)
        return Markup(('<span class="flask-moment" data-timestamp="{}" ' +
                       '{} data-refresh="{}" ' +
                       'style="display: none">{}</span>').format(
                           t, data_values, int(refresh) * 60000, t))

    def format(self, fmt=None, refresh=False):
        """Format a moment object with a custom formatting string.

        :param fmt: The formatting specification to use, as documented by the
                    ``format()`` function frommoment.js.
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("format", format=(fmt or ''), refresh=refresh)

    def fromNow(self, no_suffix=False, refresh=False):
        """Render the moment object as a relative time.

        This formatting option is often called "time ago", since it renders
        the timestamp using friendly text strings such as "2 hours ago" or
        "in 3 weeks".

        :param no_suffix: if set to ``True``, the time difference does not
                          include the suffix (the "ago" or similar).
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("fromNow", no_suffix=int(no_suffix),
                            refresh=refresh)

    def fromTime(self, timestamp, no_suffix=False, refresh=False):
        """Render the moment object as a relative time with respect to a
        given reference time.

        This function maps to the ``from()`` function from moment.js.

        :param timestamp: The reference ``datetime`` object.
        :param no_suffix: if set to ``True``, the time difference does not
                          include the suffix (the "ago" or similar).
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("from", timestamp2=self._timestamp_as_iso_8601(
            timestamp), no_suffix=int(no_suffix), refresh=refresh)

    def toNow(self, no_suffix=False, refresh=False):
        """Render the moment object as a relative time.

        This function renders as the reverse time interval of ``fromNow()``.

        :param no_suffix: if set to ``True``, the time difference does not
                          include the suffix (the "ago" or similar).
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("toNow", no_suffix=int(no_suffix), refresh=refresh)

    def toTime(self, timestamp, no_suffix=False, refresh=False):
        """Render the moment object as a relative time with respect to a
        given reference time.

        This function maps to the ``to()`` function from moment.js.

        :param timestamp: The reference ``datetime`` object.
        :param no_suffix: if set to ``True``, the time difference does not
                          include the suffix (the "ago" or similar).
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("to", timestamp2=self._timestamp_as_iso_8601(
            timestamp), no_suffix=int(no_suffix), refresh=refresh)

    def calendar(self, refresh=False):
        """Render the moment object as a relative time, either to current time
        or a given reference timestamp.

        This function renders relative time using day references such as
        tomorrow, next Sunday, etc.

        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("calendar", refresh=refresh)

    def valueOf(self, refresh=False):
        """Render the moment object as milliseconds from Unix Epoch.

        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("valueOf", refresh=refresh)

    def unix(self, refresh=False):
        """Render the moment object as seconds from Unix Epoch.

        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("unix", refresh=refresh)

    def diff(self, timestamp, units, refresh=False):
        """Render the difference between the moment object and the given
        timestamp using the provided units.

        :param timestamp: The reference ``datetime`` object.
        :param units: A time unit such as `years`, `months`, `weeks`, `days`,
                      `hours`, `minutes` or `seconds`.
        :param refresh: If set to ``True``, refresh the timestamp at one
                        minute intervals. If set to ``False``, background
                        refreshing is disabled. If set to an integer, the
                        refresh occurs at the indicated interval, given in
                        minutes.
        """
        return self._render("diff", timestamp2=self._timestamp_as_iso_8601(
            timestamp), units=units, refresh=refresh)


class Moment(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        app.extensions['moment'] = moment
        app.context_processor(self.context_processor)

    @staticmethod
    def context_processor():
        return {
            'moment': current_app.extensions['moment']
        }

    def flask_moment_js(self):
        return current_app.extensions['moment'].flask_moment_js()

    def create(self, timestamp=None):
        return current_app.extensions['moment'](timestamp)
