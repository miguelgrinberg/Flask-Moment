Flask-Moment
============

This extension enhances Jinja2 templates with formatting of dates and times using [moment.js](http://momentjs.com/).

Quick Start
-----------

Step 1: Initialize the extension:

    from flask.ext.moment import Moment
    moment = Moment(app)

Step 2: In your `<head>` section of your base template add the following code:

    <head>
        {{ moment.include_jquery() }}
        {{ moment.include_moment() }}
    </head>

Note that jQuery is required. If you are already including it on your own then you can remove the `include_jquery()` line. Secure HTTP is used if the request under which these are executed is secure.

The `include_jquery()` and `include_moment()` methods take two optional arguments. If you pass `version`, then the requested version will be loaded from the CDN. If you pass `local_js`, then the given local path will be used to load the library.

Step 3: Render timestamps in your template. For example:

    <p>The current date and time is: {{ moment().format('MMMM Do YYYY, h:mm:ss a') }}.</p>
    <p>Something happened {{ moment(then).fromTime(now) }}.</p>
    <p>{{ moment(then).calendar() }}.</p>

In the second and third examples template variables `then` and `now` are used. These must be instances of Python's `datetime` class, and <u>must be "naive" objects</u>. See the [documentation](http://docs.python.org/2/library/datetime.html) for a discussion of naive date and time objects. As an example, `now` can be set as follows:

    now = datetime.utcnow()

By default the timestamps will be converted from UTC to the local time in each client's machine before rendering. To disable the conversion to local time pass `local=True`. 
    
Note that even though the timestamps are provided in UTC the rendered dates and times will be in the local time of the client computer, so each users will always see their local time regardless of where they are located.

Function Reference
------------------

The supported list of display functions is shown below:

- `moment(timestamp=None, local=False).format(format_string)`
- `moment(timestamp=None, local=False).fromNow(no_suffix = False)`
- `moment(timestamp=None, local=False).fromTime(another_timesatmp, no_suffix = False)`
- `moment(timestamp=None, local=False).calendar()`
- `moment(timestamp=None, local=False).valueOf()`
- `moment(timestamp=None, local=False).unix()`

Consult the [moment.js documentation](http://momentjs.com/) for details on these functions.

Auto-Refresh
------------

All the display functions take an optional `refresh` argument that when set to `True` will re-render timestamps every minute. This can be useful for relative time formats such as the one returned by the `fromNow()` or `fromTime()` functions. By default refreshing is disabled.

Internationalization
--------------------

By default dates and times are rendered in English. To change to a different language add the following line in the `<head>` section after the `include_moment()` line:

    {{ moment.lang("es") }}
    
The above example sets the language to Spanish. Moment.js supports a large number of languages, consult the documentation for the list of languages and their two letter codes.

Ajax Support
------------

It is also possible to create Flask-Moment timestamps in Python code, for cases where a template is not used. This is the syntax:

    timestamp = moment.create(datetime.utcnow()).calendar()

The `moment` variable is the `Moment` instance that was created at initialization time.

A timestamp created in this way is an HTML string that can be returned as part of a response. For example, here is how a timestamp can be returned in a JSON object:

    return jsonify({ 'timestamp': moment.create(datetime.utcnow()).format('L') })

The Ajax callback in the browser needs to call `flask_moment_render_all()` each time an element containing a timestamp is added to the DOM. The included application demonstrates how this is done.
