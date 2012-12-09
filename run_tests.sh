#!/bin/sh

# naive version that doesn't run enough tests:
# python openid/test/test*.py

python3 -m unittest openid.test.test_suite
