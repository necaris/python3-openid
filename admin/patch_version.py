import sys
from os.path import abspath, join, dirname


try:
    major, minor, patch = map(int, sys.argv[1].split('.'))
except (IndexError, ValueError):
    print('Need version string of the form MAJOR.MINOR.PATCH', file=sys.stderr)
    sys.exit(1)

TARGET_FILE = abspath(join(dirname(__file__), '..', 'openid', '__init__.py'))

with open(TARGET_FILE, 'r', encoding='utf8') as f:
    lines = f.readlines()
    for i, l in enumerate(lines):
        if l.startswith('version_info'):
            l = 'version_info = ({}, {}, {})\n\n'.format(major, minor, patch)
            lines[i] = l
            break

with open(TARGET_FILE, 'w', encoding='utf8') as f:
    f.writelines(lines)
