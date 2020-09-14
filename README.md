Flask-Moment
============

[![Build Status](https://travis-ci.org/miguelgrinberg/Flask-Moment.svg?branch=master)](https://travis-ci.org/miguelgrinberg/Flask-Moment)

This extension enhances Jinja2 templates with formatting of dates and times using [moment.js](http://momentjs.com/).

Quick Start
-----------

Step 1: Initialize the extension:

    from flask_moment import Moment
    moment = Moment(app)

Step 2: In your `<head>` section of your base template add the following code:

    <head>
        {{ moment.include_jquery() }}
        {{ moment.include_moment() }}
    </head>

This extension also supports the [Flask application factory pattern](http://flask.pocoo.org/docs/latest/patterns/appfactories/) by allowing you to create a Moment object and then separately initialize it for an app:

        moment = Moment()

        def create_app(config):
            app = Flask(__name__)
            app.config.from_object(config)
            # initialize moment on the app within create_app()
            moment.init_app(app)

        app = create_app(prod_config)

Note that jQuery is required. If you are already including it on your own then you can remove the `include_jquery()` line. Secure HTTP is always used to request the external js files..

The `include_jquery()` and `include_moment()` methods take some optional arguments. If you pass a `version` argument to any of these two calls, then the requested version will be loaded from the default CDN. If you pass `local_js`, then the given local path will be used to load the library. The `include_moment()` argument takes a third argument `no_js` that when set to `True` will assume that the Moment JavaScript library is already loaded and will only add the JavaScript code that supports this extension.

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

- `moment(timestamp=None, local=False).format(format_string=None)`
- `moment(timestamp=None, local=False).fromNow(no_suffix=False)`
- `moment(timestamp=None, local=False).fromTime(another_timesatmp, no_suffix=False)`
- `moment(timestamp=None, local=False).toNow(no_suffix=False)`
- `moment(timestamp=None, local=False).toTime(another_timesatmp, no_suffix=False)`
- `moment(timestamp=None, local=False).calendar()`
- `moment(timestamp=None, local=False).valueOf()`
- `moment(timestamp=None, local=False).unix()`

Consult the [moment.js documentation](http://momentjs.com/) for details on these functions.

Auto-Refresh
------------

All the display functions take an optional `refresh` argument that when set to `True` will re-render timestamps every minute. This can be useful for relative time formats such as the one returned by the `fromNow()` or `fromTime()` functions. By default refreshing is disabled.

Default Format
--------------

The `format()` function can be invoked without arguments, in which case a default format of ISO8601 defined by the moment.js library is used. If you want to set a different default, you can set the `MOMENT_DEFAULT_FORMAT` variable in the Flask configuration. Consult the [moment.js format documentation](http://momentjs.com/docs/#/displaying/format/) for a list of accepted tokens.

Internationalization
--------------------

By default dates and times are rendered in English. To change to a different language add the following line in the `<head>` section after the `include_moment()` line:

    {{ moment.locale("es") }}
    
The above example sets the language to Spanish. Moment.js supports a large number of languages, consult the documentation for the list of languages and their two letter codes.

The extension also supports auto-detection of the client's browser language:

    {{ moment.locale(auto_detect=True) }}

Custom locales can also be included as a dictionary:

    {{ moment.locale(customizations={ ... }) }}

See the [Moment.js locale customizations](https://momentjs.com/docs/#/i18n/changing-locale/) documentation for details on how to define a custom locale.

Ajax Support
------------

It is also possible to create Flask-Moment timestamps in Python code, for cases where a template is not used. This is the syntax:

    timestamp = moment.create(datetime.utcnow()).calendar()

The `moment` variable is the `Moment` instance that was created at initialization time.

A timestamp created in this way is an HTML string that can be returned as part of a response. For example, here is how a timestamp can be returned in a JSON object:

    return jsonify({ 'timestamp': moment.create(datetime.utcnow()).format('L') })

The Ajax callback in the browser needs to call `flask_moment_render_all()` each time an element containing a timestamp is added to the DOM. The included application demonstrates how this is done.

Subresource Integrity(SRI)
-----------
[SRI ](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity) is a security feature that enables browsers to verify that resources they fetch are not maliciously manipulated. To do so a cryptographic hash is provided that proves integrity.

SRI is enabled by default. If you wish to use another version or want to host your own javascript, a [separate hash ](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity#Tools_for_generating_SRI_hashes) can be provided.
Just add `sri=<YOUR-HASH>` when calling either `moment.include_moment()` or `moment.include_jquery()`. If no sri hash is provided and you choose to use a non default version of javascript, no sri hash will be added.

You can always choose to disable sri. To do so just set `sri=False`.


Development
-----------

Currently the tests are written using pytest. 

    pip install pytest

To run the tests from the root directory use: `py.test`.

Reports on coverage with missing line numbers can be generated using pytest-cov:

    pip install pytest-cov

And then running: `py-test --cov-report term-missing --cov=flask_moment`
