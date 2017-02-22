#!/usr/bin/env python3
"""
Fetch the current TLD list from the IANA Web site, parse it, and print
an expression suitable for direct insertion into each library's trust
root validation module.

Usage:
  python gettlds.py (php|python|ruby)

Then cut-n-paste.
"""

import urllib.request
import sys

LANGS = {
    'php': (
        r"'/\.(",  # prefix
        "'",  # line prefix
        "|",  # separator
        "|' .",  # line suffix
        r")\.?$/'"  # suffix
    ),
    'python': ("['", "'", "', '", "',", "']"),
    'ruby': ("%w'", "", " ", "", "'"),
}

if __name__ == '__main__':

    lang = sys.argv[1]
    prefix, line_prefix, separator, line_suffix, suffix = LANGS[lang]

    iana_url = 'http://data.iana.org/TLD/tlds-alpha-by-domain.txt'

    with urllib.request.urlopen(iana_url) as iana_resource:
        tlds = []
        output_line = ""  # initialize a line of output

        for input_line in iana_resource:
            if input_line.startswith(b'#'):  # skip comments
                continue

            tld = input_line.decode("utf-8").strip().lower()
            nxt_output_line = output_line + prefix + tld  # update current line

            if len(nxt_output_line) > 60:
                # Long enough -- print it and reinitialize to only hold the
                # most recent TLD
                print(output_line + line_suffix)
                output_line = line_prefix + tld
            else:
                # Not long enough, so update it to the concatenated version
                output_line = nxt_output_line

            prefix = separator

    # Print the final line of remaining output
    print(output_line + suffix)
