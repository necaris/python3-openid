import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
