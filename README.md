This started out as a fork of the Python OpenID library, with changes
to make it Python 3 compatible. It's now a port of that library, including
cleanups and updates to the code in general, since I lack the patience to try and keep code compatible with Python 2.3 - 3.2.


# REQUIREMENTS

 - Python 3.x

# INSTALLATION

To install the base library, just run the following command:

    python setup.py install

To run setup.py you need the distutils module from the Python standard
library; some distributions package this seperately in a "python-dev"
package.

You can also install from PyPI with `pip`:

    pip install python3-openid


# GETTING STARTED

The examples directory includes an example server and consumer
implementation.  See the README file in that directory for more
information on running the examples. *NOTE* this may be out of date.

Library documentation is available in HTML form in the doc directory.

# LOGGING

This library offers a logging hook that will record unexpected
conditions that occur in library code. If a condition is recoverable,
the library will recover and issue a log message. If it is not
recoverable, the library will raise an exception. See the
documentation for the openid.oidutil module for more on the logging
hook.

# DOCUMENTATION

The documentation in this library is in Epydoc format, which is
detailed at:

  http://epydoc.sourceforge.net/

# CONTACT

Going forward, the plan is to maintain this library on GitHub, so any bug
reports, suggestions, and feature requests should be raised as [Issues](issues).

There are also the `#python-openid` and `#openid` channels on FreeNode IRC.
