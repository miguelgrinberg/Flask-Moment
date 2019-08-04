from distutils.version import StrictVersion
from datetime import datetime
from jinja2 import Markup
from flask import current_app

# //code.jquery.com/jquery-3.4.1.min.js
default_jquery_version = '3.4.1'
default_jquery_sri = 'sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo='

# //cdnjs.cloudflare.com/ajax/libs/moment.js/2.24.0/moment-with-locales.min.js
default_moment_version = '2.24.0'
default_moment_sri = 'sha256-AdQN98MVZs44Eq2yTwtoKufhnU+uZ7v2kXnD5vqzZVo='


class _moment(object):
    @staticmethod
    def include_moment(version=default_moment_version, local_js=None,
                       no_js=None, sri=None):
        js = ''
        if version == default_moment_version and local_js is None and \
                sri is None:
            sri = default_moment_sri
        if not no_js:
            if local_js is not None:
                if not sri:
                    js = '<script src="%s"></script>\n' % local_js
                else:
                    js = ('<script src="%s" integrity="%s" '
                          'crossorigin="anonymous"></script>\n'
                          % (local_js, sri))
            elif version is not None:
                js_filename = 'moment-with-locales.min.js' \
                    if StrictVersion(version) >= StrictVersion('2.8.0') \
                    else 'moment-with-langs.min.js'
                if not sri:
                    js = '<script src="//cdnjs.cloudflare.com/ajax/libs/' \
                         'moment.js/%s/%s"></script>\n' \
                         % (version, js_filename)
                else:
                    js = '<script src="//cdnjs.cloudflare.com/ajax/libs/' \
                         'moment.js/%s/%s" integrity="%s" ' \
                         'crossorigin="anonymous"></script>\n' \
                         % (version, js_filename, sri)

        default_format = ''
        if 'MOMENT_DEFAULT_FORMAT' in current_app.config:
            default_format = '\nmoment.defaultFormat = "%s";' % \
                current_app.config['MOMENT_DEFAULT_FORMAT']
        return Markup('''%s<script>
moment.locale("en");%s
function flask_moment_render(elem) {
    $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
    $(elem).removeClass('flask-moment').show();
}
function flask_moment_render_all() {
    $('.flask-moment').each(function() {
        flask_moment_render(this);
        if ($(this).data('refresh')) {
            (function(elem, interval) { setInterval(function() { flask_moment_render(elem) }, interval); })(this, $(this).data('refresh'));
        }
    })
}
$(document).ready(function() {
    flask_moment_render_all();
});
</script>''' % (js, default_format))  # noqa: E501

    @staticmethod
    def include_jquery(version=default_jquery_version, local_js=None,
                       sri=None):
        js = ''
        if sri is None and version == default_jquery_version and \
                local_js is None:
            sri = default_jquery_sri
        if local_js is not None:
            if not sri:
                js = '<script src="%s"></script>\n' % local_js
            else:
                js = ('<script src="%s" integrity="%s" '
                      'crossorigin="anonymous"></script>\n' % (local_js, sri))

        else:
            if not sri:
                js = ('<script src="//code.jquery.com/' +
                      'jquery-%s.min.js"></script>') % version
            else:
                js = ('<script src="//code.jquery.com/jquery-%s.min.js" '
                      'integrity="%s" crossorigin="anonymous"></script>'
                      % (version, sri))
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
                '<script>\nmoment.locale("%s", %s);\n</script>' % (
                    language, customization))
        return Markup(
            '<script>\nmoment.locale("%s");\n</script>' % language)

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

    def _render(self, format, refresh=False):
        t = self._timestamp_as_iso_8601(self.timestamp)
        return Markup(('<span class="flask-moment" data-timestamp="%s" ' +
                       'data-format="%s" data-refresh="%d" ' +
                       'style="display: none">%s</span>') %
                      (t, format, int(refresh) * 60000, t))

    def format(self, fmt=None, refresh=False):
        return self._render("format('%s')" % (fmt or ''), refresh)

    def fromNow(self, no_suffix=False, refresh=False):
        return self._render("fromNow(%s)" % int(no_suffix), refresh)

    def fromTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("from(moment('%s'),%s)" %
                            (self._timestamp_as_iso_8601(timestamp),
                             int(no_suffix)), refresh)

    def calendar(self, refresh=False):
        return self._render("calendar()", refresh)

    def valueOf(self, refresh=False):
        return self._render("valueOf()", refresh)

    def unix(self, refresh=False):
        return self._render("unix()", refresh)


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
