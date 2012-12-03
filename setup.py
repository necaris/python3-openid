import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Python 3 support
extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
        use_2to3_fixers=['custom_fixers']
    )


if 'sdist' in sys.argv:
    os.system('./admin/makedoc')

version = '[library version:2.2.5]'[17:-1]

setup(
    name='python-openid',
    version=version,
    description='OpenID support for servers and consumers.',
    long_description='''This is a set of Python packages to support use of
the OpenID decentralized identity system in your application.  Want to enable
single sign-on for your web site?  Use the openid.consumer package.  Want to
run your own OpenID server? Check out openid.server.  Includes example code
and support for a variety of storage back-ends.''',
    url='http://github.com/openid/python-openid',
    packages=['openid',
              'openid.consumer',
              'openid.server',
              'openid.store',
              'openid.yadis',
              'openid.extensions',
              'openid.extensions.draft',
              ],
    # license specified by classifier.
    # license=getLicense(),
    author='JanRain',
    author_email='openid@janrain.com',
    download_url='http://github.com/openid/python-openid/tarball/%s' % (version,),
    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    **extra
    )
