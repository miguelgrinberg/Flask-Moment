Advanced options
----------------

Auto-Refresh
~~~~~~~~~~~~

All the display functions take an optional ``refresh`` argument that when set
to ``True`` will re-render timestamps every minute. If a different time
interval is desired, pass the interval in minutes as the value of the
``refresh`` argument.

This option is useful for relative time formats such as the one returned by
the ``fromNow()`` or ``fromTime()`` functions. For example, the date of a
comment would appear as "a few seconds ago" when the comment was just entered,
but a minute later it would automatically refresh to "a minute ago" without
the need to refresh the page.

By default automatic refreshing is disabled.

Default Format
~~~~~~~~~~~~~~

The ``format()`` function can be invoked without arguments, in which case a
default format of ISO8601 defined by the moment.js library is used. If you
want to set a different default, you can set the ``MOMENT_DEFAULT_FORMAT``
variable in the Flask configuration. Consult the
`moment.js format documentation <https://momentjs.com/docs/#/displaying/format/>`_
for a list of accepted tokens.

Internationalization
~~~~~~~~~~~~~~~~~~~~

By default dates and times are rendered in English. To change to a different
language add the following line in the ``<head>`` section of your template(s),
after the ``include_moment()`` line::

    {{ moment.locale("es") }}
    
The above example sets the language to Spanish. Moment.js supports a large
number of languages. Consult the documentation for the list of languages and
their corresponding two letter codes.

This extension also supports auto-detection of the client's browser language::

    {{ moment.locale(auto_detect=True) }}

Custom locales can also be included as a dictionary::

    {{ moment.locale(customizations={ ... }) }}

See the `moment.js locale customizations <https://momentjs.com/docs/#/i18n/changing-locale/>`_
documentation for details on how to define a custom locale.

Ajax Support
~~~~~~~~~~~~

It is also possible to create Flask-Moment timestamps in Python code that is
invoked from the client page through Ajax, without the use of Jinja templates::


    timestamp = moment.create(datetime.utcnow()).calendar()

The ``moment`` variable is the ``Moment`` instance that was created at
initialization time.

A timestamp created in this way is an HTML string that can be returned as part
of a response. For example, here is how a timestamp can be returned in a JSON
object::

    return { 'timestamp': moment.create(datetime.utcnow()).format('L') }

The Ajax callback in the browser needs to call ``flask_moment_render_all()``
each time an element containing a timestamp is added to the DOM. The example
application in the Flask-Moment GitHub repository demonstrates how this is
done.

Subresource Integrity (SRI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`SRI <https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity>`_
is a security feature that enables browsers to verify that resources they
fetch are not maliciously manipulated. To do so a cryptographic hash is
provided that proves integrity.

SRI for the moment.js library is enabled by default. If you wish to use
a version different than the one bundled with this extension, or want to host
your own javascript, a `separate hash <https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity#tools_for_generating_sri_hashes>`_
can be provided.

Just add ``sri=<YOUR-HASH>`` when calling ``moment.include_moment()``. If no
SRI hash is provided when a custom moment.js version is used, then SRI
verification is not used.

To disable SRI, pass ``sri=False`` in the ``include_moment()`` call.
