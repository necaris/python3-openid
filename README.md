This started out as a fork of the Python OpenID library, with changes
to make it Python 3 compatible. It's now a port of that library, including
cleanups and updates to the code in general.

[![Build Status](https://travis-ci.org/necaris/python3-openid.png?branch=master)](https://travis-ci.org/necaris/python3-openid)

# REQUIREMENTS

 - Python 3.x (tested on 3.2, 3.3)

# INSTALLATION

The recommended way is to install from PyPI with `pip`:

    pip install python3-openid

Alternatively, you can run the following command:

    python setup.py install


# GETTING STARTED

The examples directory includes an example server and consumer
implementation.  See the README file in that directory for more
information on running the examples. *NOTE* this may be out of date.

The library should follow the existing `python-openid` API as closely as possible -- documentation will be auto-generated as soon as I can figure out how to update the documentation tools.

# LOGGING

This library offers a logging hook that will record unexpected
conditions that occur in library code. If a condition is recoverable,
the library will recover and issue a log message. If it is not
recoverable, the library will raise an exception. See the
documentation for the `openid.oidutil` module for more on the logging
hook.

# DOCUMENTATION

The documentation in this library is in Epydoc format, which is
detailed at:

  http://epydoc.sourceforge.net/

# CONTACT

Going forward, the plan is to maintain this library on GitHub, so any bug
reports, suggestions, and feature requests should be raised as Issues.

There are also the `#python-openid` and `#openid` channels on FreeNode IRC.
