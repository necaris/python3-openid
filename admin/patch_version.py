#!/usr/bin/env python3
"""
Update the `version_info` embedded in the library to the given version.
"""
import sys
from os.path import abspath, join, dirname

if __name__ == '__main__':
    try:
        major, minor, patch = map(int, sys.argv[1].split('.'))
    except (IndexError, ValueError):
        print('Need version string in form MAJOR.MINOR.PATCH', file=sys.stderr)
        sys.exit(1)

    TARGET = abspath(join(dirname(__file__), '..', 'openid', '__init__.py'))

    with open(TARGET, 'r', encoding='utf8') as f:
        lines = f.readlines()
        for i, l in enumerate(lines):
            if l.startswith('version_info'):
                v_info = '({}, {}, {})'.format(major, minor, patch)
                lines[i] = 'version_info = {}\n\n'.format(v_info)
                break

    with open(TARGET, 'w', encoding='utf8') as f:
        f.writelines(lines)
