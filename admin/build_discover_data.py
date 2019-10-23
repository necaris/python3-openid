#!/usr/bin/env python3
"""
Build a set of YADIS identity URL / service discovery files in
the format for Apache mod_asis -- simple text files containing their
own HTTP headers.

These can then be used as a basis for testing.
"""

import sys
import os.path
import urllib.parse

from openid.test import discoverdata

manifest_header = """\
# This file contains test cases for doing YADIS identity URL and
# service discovery. For each case, there are three URLs. The first
# URL is the user input. The second is the identity URL and the third
# is the URL from which the XRDS document should be read.
#
# The file format is as follows:
# User URL <tab> Identity URL <tab> XRDS URL <newline>
#
# blank lines and lines starting with # should be ignored.
#
# To use this test:
#
# 1. Run your discovery routine on the User URL.
#
# 2. Compare the identity URL returned by the discovery routine to the
#    identity URL on that line of the file. It must be an EXACT match.
#
# 3. Do a regular HTTP GET on the XRDS URL. Compare the content that
#    was returned by your discovery routine with the content returned
#    from that URL. It should also be an exact match.

"""


def buildDiscover(base_url, out_dir):
    """
    Convert all files in a directory to apache mod_asis files in
    another directory.
    """
    test_data = discoverdata.readTests(discoverdata.default_test_file)

    def writeTestFile(test_name):
        """Helper to generate an output data file for a given test name."""
        template = test_data[test_name]

        data = discoverdata.fillTemplate(test_name, template, base_url,
                                         discoverdata.example_xrds)

        out_file_name = os.path.join(out_dir, test_name)
        with open(out_file_name, 'w', encoding="utf-8") as out_file:
            out_file.write(data)

    manifest = [manifest_header]
    for success, input_name, id_name, result_name in discoverdata.testlist:
        if not success:
            continue
        writeTestFile(input_name)

        input_url = urllib.parse.urljoin(base_url, input_name)
        id_url = urllib.parse.urljoin(base_url, id_name)
        result_url = urllib.parse.urljoin(base_url, result_name)

        manifest.append('\t'.join((input_url, id_url, result_url)))
        manifest.append('\n')

    manifest_file_name = os.path.join(out_dir, 'manifest.txt')
    with open(manifest_file_name, 'w', encoding="utf-8") as manifest_file:
        for chunk in manifest:
            manifest_file.write(chunk)


if __name__ == '__main__':
    buildDiscover(*sys.argv[1:])
