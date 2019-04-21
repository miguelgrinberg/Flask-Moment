from distutils.version import StrictVersion
from datetime import datetime
from jinja2 import Markup
from flask import current_app


class _moment(object):
    @staticmethod
    def include_moment(version='2.18.1', local_js=None, no_js=None, sri=None):
        js = ''
        if version == '2.18.1' and local_js is None and sri is None:
            sri = ('sha384-iMhq1oHAQWG7+cVzHBvYynTbGZy'
                   'O4DniLR7bhY1Q39AMn8ePTV9uByV/06g2xqOS')
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
    def include_jquery(version='2.1.0', local_js=None, sri=None):
        js = ''
        if sri is None and version == '2.1.0' and local_js is None:
            sri = ('sha384-85/BFduEdDxQ86xztyNu4BBkVZmlv'
                   'u+iB7zhBu0VoYdq+ODs3PKpU6iVE3ZqPMut')
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
