"""
Django settings for djopenid example project
"""
import os
import sys
import warnings

try:
    import openid
except ImportError as e:
    warnings.warn(
        "Could not import OpenID.  Please consult the djopenid README.")
    sys.exit(1)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (  # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# NOTE that this is a sample configuration and probably not suitable for
# production use in any way, shape or form.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': './sqlite.db'
    }
}

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us.UTF-8'
USE_I18N = False

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u^bw6lmsa6fah0$^lz-ct$)y7x7#ag92-z+y45-8!(jk0lkavy'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader', )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware', )

ROOT_URLCONF = 'djopenid.urls'

TEMPLATE_CONTEXT_PROCESSORS = ()

TEMPLATE_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')), )

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # These are the example OpenID consumer and server
    'djopenid.consumer',
    'djopenid.server', )
