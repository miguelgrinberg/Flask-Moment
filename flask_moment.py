from distutils.version import StrictVersion
from datetime import datetime
from jinja2 import Markup
from flask import current_app
from functools import lru_cache
import hashlib
import base64
import urllib.request


class _moment(object):

    @staticmethod
    def include_moment(version='2.18.1', local_js=None, no_js=None, sri=False):
        js = ''
        if not no_js:
            if local_js is not None:
                js = '<script src="%s"></script>\n' % local_js
            elif version is not None:
                js_filename = 'moment-with-locales.min.js' \
                    if StrictVersion(version) >= StrictVersion('2.8.0') \
                    else 'moment-with-langs.min.js'
                if sri:
                    path = 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/%s/%s' % (version, js_filename)
                    h_64 = _moment._sri_hash(_moment._get_data(
                        '%s' % path))
                    js = '<script src="%s" integrity="%s" crossorigin="anonymous"></script>\n' % (path, h_64)
                else:
                    js = '<script src="//cdnjs.cloudflare.com/ajax/libs/' \
                         'moment.js/%s/%s"></script>\n' % (version, js_filename)
        return Markup('''%s<script>
moment.locale("en");
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
</script>''' % js)  # noqa: E501

    @staticmethod
    def include_jquery(version='2.1.0', local_js=None, sri=False):
        js = ''
        if local_js is not None:
            js = '<script src="%s"></script>\n' % local_js
        else:
            if sri:
                path = 'https://code.jquery.com/jquery-%s.min.js' % version
                h_64 = _moment._sri_hash(_moment._get_data(path))
                js = '<script src="%s" integrity="%s" crossorigin="anonymous"></script>' % (path, h_64)
            else:
                js = ('<script src="//code.jquery.com/' +
                      'jquery-%s.min.js"></script>') % version
        return Markup(js)

    @staticmethod
    def locale(language='en', auto_detect=False):
        if auto_detect:
            return Markup('<script>\nvar locale = '
                          'window.navigator.userLanguage || '
                          'window.navigator.language;\n'
                          'moment.locale(locale);\n</script>')
        else:
            return Markup(
                '<script>\nmoment.locale("%s");\n</script>' % language)

    @staticmethod
    def lang(language):
        return _moment.locale(language)

    @staticmethod
    @lru_cache()
    def _sri_hash(data):
        print("Hashing..")
        h = hashlib.sha384(data).digest()
        h_64 = base64.b64encode(h).decode()
        return 'sha384-{}'.format(h_64)

    @staticmethod
    @lru_cache()
    def _get_data(url):
        response = urllib.request.urlopen(url)
        data = response.read()
        return data

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

    def format(self, fmt, refresh=False):
        return self._render("format('%s')" % fmt, refresh)

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
