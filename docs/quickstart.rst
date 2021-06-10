Quick Start
-----------

Installation and configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the extension with ``pip``::


    pip install flask-moment

Once the extension is installed, create an instance and initialize it with the
Flask application::

    from flask_moment import Moment
    moment = Moment(app)

If the application uses the `application factory pattern <https://flask.palletsprojects.com/en/latest/patterns/appfactories/>`_,
the two-step initialization method can be used instead::

    moment = Moment()

    def create_app():
        app = Flask(__name__)
        moment.init_app(app)
        return app

    app = create_app(prod_config)

To complete the initialization, add the following line inside the ``<head>``
section of the template(s) that will use the extension::

    {{ moment.include_moment() }}

If you use template inheritance, the best place to add this line is in your
base template.

Note that older versions of this extension required jQuery, but this isn't the
case anymore. The ``include_jquery()`` function that existed in older releases
has now been removed.

The ``include_moment()`` function accepts a few arguments that control settings
such as the version of ``moment.js`` to use, or wether the library should be
imported from a CDN.

Rendering timestamps with Flask-Moment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To render a date with Flask-Moment, use the ``moment()`` function with one of
the available formatting options. The following example uses a custom format
string to render the current time::

    <p>Current date and time: {{ moment().format('MMMM Do YYYY, h:mm:ss a') }}.</p>

To render a timestamp other than the current time, pass a ``datetime`` object
as an argument to the ``moment()`` function::

    <p>Date: {{ moment(date).format('LL') }}</p>

Some of the rendering functions render the ellapsed time between a datetime 
object and current time. The following example renders a timestamp in a
"time ago" style::

    <p>{{ author }} said {{ moment(comment_datetime).fromNow() }}</p>
