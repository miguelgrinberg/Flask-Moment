from distutils.version import StrictVersion
from datetime import datetime
from markupsafe import Markup
from flask import current_app

# //cdnjs.cloudflare.com/ajax/libs/moment.js/2.27.0/moment-with-locales.min.js
default_moment_version = '2.29.1'
default_moment_sri = ('sha512-LGXaggshOkD/at6PFNcp2V2unf9LzFq6LE+sChH7ceMTDP0'
                      'g2kn6Vxwgg7wkPP7AAtX+lmPqPdxB47A0Nz0cMQ==')


class _moment(object):
    @staticmethod
    def include_moment(version=default_moment_version, local_js=None,
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
                    js = ('<script src="https://cdnjs.cloudflare.com/ajax/'
                          'libs/moment.js/{}/{}"></script>\n').format(
                              version, js_filename)
                else:
                    js = ('<script src="https://cdnjs.cloudflare.com/ajax/'
                          'libs/moment.js/{}/{}" integrity="{}" '
                          'crossorigin="anonymous"></script>\n').format(
                              version, js_filename, sri)

        default_format = ''
        if 'MOMENT_DEFAULT_FORMAT' in current_app.config:
            default_format = '\nmoment.defaultFormat = "{}";'.format(
                current_app.config['MOMENT_DEFAULT_FORMAT'])
        return Markup('''{}<script>
moment.locale("en");{}
function flask_moment_render(elem) {{
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
        if (refresh) {{
            (function(elem, interval) {{
                setInterval(function() {{
                    flask_moment_render(elem);
                }}, interval);
            }})(moment, refresh);
        }}
    }})
}}
document.addEventListener("DOMContentLoaded", flask_moment_render_all);
</script>'''.format(js, default_format))  # noqa: E501

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
        return self._render("format", format=(fmt or ''), refresh=refresh)

    def fromNow(self, no_suffix=False, refresh=False):
        return self._render("fromNow", no_suffix=int(no_suffix),
                            refresh=refresh)

    def fromTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("from", timestamp2=self._timestamp_as_iso_8601(
            timestamp), no_suffix=int(no_suffix), refresh=refresh)

    def toNow(self, no_suffix=False, refresh=False):
        return self._render("toNow", no_suffix=int(no_suffix), refresh=refresh)

    def toTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("to", timestamp2=self._timestamp_as_iso_8601(
            timestamp), no_suffix=int(no_suffix), refresh=refresh)

    def calendar(self, refresh=False):
        return self._render("calendar", refresh=refresh)

    def valueOf(self, refresh=False):
        return self._render("valueOf", refresh=refresh)

    def unix(self, refresh=False):
        return self._render("unix", refresh=refresh)

    def diff(self, timestamp, units, refresh=False):
        return self._render("diff", timestamp2=self._timestamp_as_iso_8601(
            timestamp), units=units, refresh=refresh)


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
