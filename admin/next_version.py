#!/usr/bin/env python3
"""
Compute the next release version of the library, using `--major`, `--minor`,
or `--patch` arguments to determine the level at which the version is to be
incremented.
"""
import sys
from os.path import abspath, join, dirname

if __name__ == '__main__':
    sys.path.append(abspath(join(dirname(__file__), '..')))

    import openid

    major, minor, patch = openid.version_info
    pieces = None

    if '--major' in sys.argv:
        pieces = (major + 1, 0, 0)
    elif '--minor' in sys.argv:
        pieces = (major, minor + 1, 0)
    elif '--patch' in sys.argv:
        pieces = (major, minor, patch + 1)

    if pieces:
        print('.'.join(map(str, pieces)), end='')
    else:
        print('Major, minor, or patch?', file=sys.stderr)
        sys.exit(1)
