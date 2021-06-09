# Flask-Moment change log

**Release 0.11.0** - 2020-12-17

- Update default moment version and hash [#67](https://github.com/miguelgrinberg/flask-moment/issues/67) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/f4ceefbdab6c9dcf1449127e7cdf7a3aa0049da3)) (thanks **Irakliy Krasnov**!)
- Always use `https://` to request the JavaScript files from the CDN [#65](https://github.com/miguelgrinberg/flask-moment/issues/65) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/a8f42fce6b1f50b73694830975a29bb30d95efdd)) (thanks **Vicki Jackson**!)
- Update moment.js and add option to use Moment.js without locales [#63](https://github.com/miguelgrinberg/flask-moment/issues/63) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/5472239042d674809fc62dd3112d52f8154d3ec9)) (thanks **Steven van de Graaf**!)

**Release 0.10.0** - 2020-06-10

- Various code and test improvements, also add python 3.7 and 3.8 to build ([commit](https://github.com/miguelgrinberg/flask-moment/commit/842185179d2b89f895281b0b4077a8eabeba6f83))
- Remove use of JavaScript eval[#60](https://github.com/miguelgrinberg/flask-moment/issues/60) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/5e453fc0e9a0947662ceaa0fca50cab090ca3811)) (thanks **Emilien Klein**!)
- Docs: Fix simple typo, acepted -> accepted [#58](https://github.com/miguelgrinberg/flask-moment/issues/58) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/e506753ffe9d0b5200173f714c0294754b685699)) (thanks **Tim Gates**!)
- Add `toTime` and `toNow` to display functions [#57](https://github.com/miguelgrinberg/flask-moment/issues/57) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/13ba7ee3b0ab8d0e7aa774781ef3b3ec33cad9ce)) (thanks **Mohamed Feddad**!)

**Release 0.9.0** - 2019-08-04

- Updated requirements in example application ([commit](https://github.com/miguelgrinberg/flask-moment/commit/28a5fdbcffcd8b6ed03d9e67bdbf31328b57e2d6))
- Add support of customization object for the method moment.locale [#50](https://github.com/miguelgrinberg/flask-moment/issues/50) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/5b274132604f6e2d8dd5b4c7adb221b17c42c817)) (thanks **Aleksandr**!)

**Release 0.8.0** - 2019-06-16

- Default format [#48](https://github.com/miguelgrinberg/flask-moment/issues/48) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/8786663286806668eab3683458aa3390d505484b)) (thanks **jacobthetechy**!)
- Simplify tests and handling of js versions ([commit](https://github.com/miguelgrinberg/flask-moment/commit/1b273c445957ea507ee23926dfa17be111b74fd7))
- Add SRI v2.0 [#42](https://github.com/miguelgrinberg/flask-moment/issues/42) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/d87eaf8e485757a871928e5248d07a586abfd5fc)) (thanks **M0r13n**!)

**Release 0.7.0** - 2019-02-16

- Added `no_js` argument to `include_moment` ([commit](https://github.com/miguelgrinberg/flask-moment/commit/d99f9ba7c393fa120afff10a9bded11d09a303d5))
- Fix license declaration in setup.py ([commit](https://github.com/miguelgrinberg/flask-moment/commit/243d8e0d523e4f060a7c2cf1ce7b8135bdcefaf1))

**Release 0.6.0** - 2017-12-28

- Fix travis build ([commit](https://github.com/miguelgrinberg/flask-moment/commit/d0468b770d2cbdedf92e051053793c186eb9f6ba))
- Add auto-detect locale support [#33](https://github.com/miguelgrinberg/flask-moment/issues/33) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/32e18b6fc6594ba34281cef04356a5d24bfdf5a2)) (thanks **Grey Li**!)
- Fixed unit tests ([commit](https://github.com/miguelgrinberg/flask-moment/commit/6503a2f53cccba498df9675f3ebceaae01dc5c1c))

**Release 0.5.2** - 2017-09-29

- Bump moment.js version to 2.18.1 ([commit](https://github.com/miguelgrinberg/flask-moment/commit/c412f13e1235ab4ec5f07fd01a8dcf56b9a7ad51))
- Travis build badge ([commit](https://github.com/miguelgrinberg/flask-moment/commit/bbd622383b63892702f337772e45f1443bf610c7))
- A few unit test fixes, plus tox/travis builds ([commit](https://github.com/miguelgrinberg/flask-moment/commit/71f46e56ff60d2ae66f189909de3544d7aca35ec))
- Add tests for the basic features [#28](https://github.com/miguelgrinberg/flask-moment/issues/28) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/e908e2befa456f4fd886845e52060b643b3ecf04)) (thanks **Kyle Lawlor**!)
- Added example of how to setup Flask-Moment using a Flask app factory ([commit](https://github.com/miguelgrinberg/flask-moment/commit/5a27fff48864d7233b05936b54edbc3212f0938d)) (thanks **Jeff Widman**!)
- Switched imports from deprecated `flask.ext.extensionname` format to `flask_extensionname` ([commit](https://github.com/miguelgrinberg/flask-moment/commit/32f8efc9079a5e7eedf05abba72d42ffc806d4c3)) (thanks **Jeff Widman**!)

**Release 0.5.1** - 2015-08-06

- Hide timestamps until rendering is complete [#16](https://github.com/miguelgrinberg/flask-moment/issues/16) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/a5d312f789949e352845dd1f767e98a8e428b3eb)) (thanks **Cole Kettler**!)
- Upgrading the default version to the latest moment.js release(2.10.3) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/56102d5b53c8d2b95b3684661517cc0cb2a6c713)) (thanks **small-yellow-rice**!)

**Release 0.4.0**

- Added `local_js` option to `include_moment()` and `include_jquery()` ([commit](https://github.com/miguelgrinberg/flask-moment/commit/8bd3035ec4d234ac7617e22e46efc06936cd0db2))
- pep8 fixes ([commit](https://github.com/miguelgrinberg/flask-moment/commit/ff63a40e97c91a1432101125c6b26cc40f2b62d2))

**Release 0.3.3**

- Correct fix for [#8](https://github.com/miguelgrinberg/flask-moment/issues/8) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/0d3dcd8a550bb7961d3a1469ed80b24bcf277466))

**Release 0.3.2**

- Correct `include_moment(version=None)` handling [#8](https://github.com/miguelgrinberg/flask-moment/issues/8) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/e59dae390e4fccb30ef761ff18e29803fe3d9e57))

**Release 0.3.1**

- Fixed https support ([commit](https://github.com/miguelgrinberg/flask-moment/commit/1ccf8aec18f3325eb9d74468f904cd10b9c31f27)) (thanks **Tal Shiri**!)

**Release 0.3**

- Added "local" argument to `moment()` constructor to disable conversion from UTC to local time ([commit](https://github.com/miguelgrinberg/flask-moment/commit/3afcbc6290494402b420a0a98bae2be94a7565f1))
- Use secure URLs when request is secure [#2](https://github.com/miguelgrinberg/flask-moment/issues/2) ([commit](https://github.com/miguelgrinberg/flask-moment/commit/0ee69da4408171168c6c0fe84d6f437ab4e8031f))

**Release 0.2**

- First public version 
