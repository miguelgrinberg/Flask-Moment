"""
Flask-Moment
------------

Formatting of dates and times in Flask templates using moment.js.
"""
from setuptools import setup


setup(
    name='Flask-Moment',
    version='0.10.0',
    url='http://github.com/miguelgrinberg/flask-moment/',
    license='MIT',
    author='Miguel Grinberg',
    author_email='miguelgrinberg50@gmail.com',
    description='Formatting of dates and times in Flask templates using moment.js.',
    long_description=__doc__,
    py_modules=['flask_moment'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
