from datetime import datetime
import json
from jinja2 import Markup
from flask import current_app, request

class _moment(object):
    @staticmethod
    def include_moment(version = '2.3.1'):
        if version is not None:
            if request.is_secure:
                protocol = 'https'
            else:
                protocol = 'http'
            js = '<script src="%s://cdnjs.cloudflare.com/ajax/libs/moment.js/%s/moment-with-langs.min.js"></script>\n' % (protocol, version)
        return Markup('''%s<script>
function flask_moment_render(elem) {
    $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
    $(elem).removeClass('flask-moment');
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
</script>''' % js)

    @staticmethod
    def include_jquery(version = '1.10.1'):
        if request.is_secure:
            protocol = 'https'
        else:
            protocol = 'http'
        return Markup('<script src="%s://code.jquery.com/jquery-%s.min.js"></script>' % (protocol, version))

    @staticmethod
    def lang(language):
        return Markup('<script>\nmoment.lang("%s");\n</script>' % language)

    def __init__(self, timestamp = None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

    def _timestamp_as_iso_8601(self, timestamp):
        return timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _render(self, format, refresh = False):
        t = self._timestamp_as_iso_8601(self.timestamp)
        return Markup('<span class="flask-moment" data-timestamp="%s" data-format="%s" data-refresh="%d">%s</span>' % (t, format, int(refresh) * 60000, t))

    def format(self, fmt, refresh = False):
        return self._render("format('%s')" % fmt, refresh)

    def fromNow(self, no_suffix = False, refresh = False):
        return self._render("fromNow(%s)" % int(no_suffix), refresh)

    def fromTime(self, timestamp, no_suffix = False, refresh = False):
        return self._render("from(moment('%s'),%s)" % (self._timestamp_as_iso_8601(timestamp),int(no_suffix)), refresh)

    def calendar(self, refresh = False):
        return self._render("calendar()", refresh)

    def valueOf(self, refresh = False):
        return self._render("valueOf()", refresh)

    def unix(self, refresh = False):
        return self._render("unix()", refresh)

class Moment(object):
    def __init__(self, app = None):
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

    def create(self, timestamp = None):
        return current_app.extensions['moment'](timestamp)
