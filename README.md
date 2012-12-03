This started out as a fork of the Python OpenID library, with changes
to make it Python 3 compatible. It's now a port of that library, including
cleanups and updates to the code in general, since I unfortunately lack
the patience to try and keep code compatible with Python 2.3 - 3.2.


REQUIREMENTS
============

 - Python 3.x

INSTALLATION
============

To install the base library, just run the following command:

python setup.py install

To run setup.py you need the distutils module from the Python standard
library; some distributions package this seperately in a "python-dev"
package.


GETTING STARTED
===============

The examples directory includes an example server and consumer
implementation.  See the README file in that directory for more
information on running the examples.

Library documentation is available in html form in the doc directory.


LOGGING
=======

This library offers a logging hook that will record unexpected
conditions that occur in library code. If a condition is recoverable,
the library will recover and issue a log message. If it is not
recoverable, the library will raise an exception. See the
documentation for the openid.oidutil module for more on the logging
hook.


DOCUMENTATION
=============

The documentation in this library is in Epydoc format, which is
detailed at:

  http://epydoc.sourceforge.net/


CONTACT
=======

Send bug reports, suggestions, comments, and questions to
http://openid.net/developers/dev-mailing-lists/.

If you have a bugfix or feature you'd like to contribute, don't
hesitate to send it to us.  For more detailed information on how to
contribute, see

  http://openidenabled.com/contribute/
