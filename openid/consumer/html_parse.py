"""
This module implements a VERY limited parser that finds <link> tags in
the head of HTML or XHTML documents and parses out their attributes
according to the OpenID spec. It is a liberal parser, but it requires
these things from the data in order to work:

 - There must be an open <html> tag

 - There must be an open <head> tag inside of the <html> tag

 - Only <link>s that are found inside of the <head> tag are parsed
   (this is by design)

 - The parser follows the OpenID specification in resolving the
   attributes of the link tags. This means that the attributes DO NOT
   get resolved as they would by an XML or HTML parser. In particular,
   only certain entities get replaced, and href attributes do not get
   resolved relative to a base URL.

From http://openid.net/specs.bml#linkrel:

 - The openid.server URL MUST be an absolute URL. OpenID consumers
   MUST NOT attempt to resolve relative URLs.

 - The openid.server URL MUST NOT include entities other than &amp;,
   &lt;, &gt;, and &quot;.

The parser ignores SGML comments and <![CDATA[blocks]]>. Both kinds of
quoting are allowed for attributes.

The parser deals with invalid markup in these ways:

 - Tag names are not case-sensitive

 - The <html> tag is accepted even when it is not at the top level

 - The <head> tag is accepted even when it is not a direct child of
   the <html> tag, but a <html> tag must be an ancestor of the <head>
   tag

 - <link> tags are accepted even when they are not direct children of
   the <head> tag, but a <head> tag must be an ancestor of the <link>
   tag

 - If there is no closing tag for an open <html> or <head> tag, the
   remainder of the document is viewed as being inside of the tag. If
   there is no closing tag for a <link> tag, the link tag is treated
   as a short tag. Exceptions to this rule are that <html> closes
   <html> and <body> or <head> closes <head>

 - Attributes of the <link> tag are not required to be quoted.

 - In the case of duplicated attribute names, the attribute coming
   last in the tag will be the value returned.

 - Any text that does not parse as an attribute within a link tag will
   be ignored. (e.g. <link pumpkin rel='openid.server' /> will ignore
   pumpkin)

 - If there are more than one <html> or <head> tag, the parser only
   looks inside of the first one.

 - The contents of <script> tags are ignored entirely, except unclosed
   <script> tags. Unclosed <script> tags are ignored.

 - Any other invalid markup is ignored, including unclosed SGML
   comments and unclosed <![CDATA[blocks.
"""

__all__ = ['parseLinkAttrs']

import re

flags = (
    re.DOTALL  # Match newlines with '.'
    | re.IGNORECASE | re.VERBOSE  # Allow comments and whitespace in patterns
    | re.UNICODE  # Make \b respect Unicode word boundaries
)

# Stuff to remove before we start looking for tags
removed_re = re.compile(r'''
  # Comments
  <!--.*?-->

  # CDATA blocks
| <!\[CDATA\[.*?\]\]>

  # script blocks
| <script\b

  # make sure script is not an XML namespace
  (?!:)

  [^>]*>.*?</script>

''', flags)


# Linear, exact replacement for removed_re.sub('', html).  A lazy pair "O...C"
# means the first O, then the first C after it, which a fixed-string search
# gives directly.  The one subtlety is that when an O cannot complete, the
# regex keeps looking for a later O - but if a C is absent from the rest of the
# string, no later O of that kind can complete either, so that kind is retired.
_comment_open = re.compile(r'<!--')
_comment_close = re.compile(r'-->')
_cdata_open = re.compile(r'<!\[CDATA\[', re.IGNORECASE)
_cdata_close = re.compile(r'\]\]>')
_script_lit = re.compile(r'<script', re.IGNORECASE)
_script_head = re.compile(r'<script\b(?!:)', re.IGNORECASE | re.UNICODE)
_script_gt = re.compile(r'>')
_script_close = re.compile(r'</script>', re.IGNORECASE)


def _script_span(html, start):
    """Span of the leftmost ``<script...>...</script>`` at or after start."""
    pos = start
    while True:
        mo = _script_lit.search(html, pos)
        if mo is None:
            return None
        if _script_head.match(html, mo.start()) is None:
            # Not a tag: a longer word, or the "script:" XML namespace.
            pos = mo.start() + 1
            continue
        gt = _script_gt.search(html, mo.end())
        if gt is None:
            return None  # no ">" left, so no later opener can complete either
        close = _script_close.search(html, gt.end())
        if close is None:
            return None  # no closer left, same reasoning
        return mo.start(), close.end()


def removeMarkup(html):
    """Remove comments, CDATA blocks and script blocks, as removed_re does."""
    out = []
    copied = pos = 0
    live_comment = live_cdata = live_script = True
    while pos < len(html):
        best = None
        if live_comment:
            mo = _comment_open.search(html, pos)
            close = None if mo is None else _comment_close.search(html, mo.end())
            if close is None:
                live_comment = False
            else:
                best = (mo.start(), close.end())
        if live_cdata:
            mo = _cdata_open.search(html, pos)
            close = None if mo is None else _cdata_close.search(html, mo.end())
            if close is None:
                live_cdata = False
            elif best is None or mo.start() < best[0]:
                best = (mo.start(), close.end())
        if live_script:
            span = _script_span(html, pos)
            if span is None:
                live_script = False
            elif best is None or span[0] < best[0]:
                best = span
        if best is None:
            break
        out.append(html[copied:best[0]])
        copied = pos = best[1]
    out.append(html[copied:])
    return ''.join(out)


tag_expr = r'''
# Starts with the tag name at a word boundary, where the tag name is
# not a namespace
<%(tag_name)s\b(?!:)

# All of the stuff up to a ">", hopefully attributes.
(?P<attrs>[^>]*?)

(?: # Match a short tag
    />

|   # Match a full tag
    >

    (?P<contents>.*?)

    # Closed by
    (?: # One of the specified close tags
        </?%(closers)s\s*>

        # End of the string
    |   \Z

    )

)
'''


def tagMatcher(tag_name, *close_tags):
    if close_tags:
        options = '|'.join((tag_name, ) + close_tags)
        closers = '(?:%s)' % (options, )
    else:
        closers = tag_name

    expr = tag_expr % locals()
    return re.compile(expr, flags)


# Must contain at least an open html and an open head tag
html_find = tagMatcher('html')
head_find = tagMatcher('head', 'body')
link_find = re.compile(r'<link\b(?!:)', flags)

attr_find = re.compile(r'''
# Must start with a sequence of word-characters, followed by an equals sign
(?P<attr_name>\w+)=

# Then either a quoted or unquoted attribute
(?:

 # Match everything that\'s between matching quote marks
 (?P<qopen>["\'])(?P<q_val>.*?)(?P=qopen)
|

 # If the value is not quoted, match up to whitespace
 (?P<unq_val>(?:[^\s<>/]|/(?!>))+)
)

|

(?P<end_link>[<>])
''', flags)

# Entity replacement:
replacements = {
    'amp': '&',
    'lt': '<',
    'gt': '>',
    'quot': '"',
}

ent_replace = re.compile(r'&(%s);' % '|'.join(list(replacements.keys())))


def replaceEnt(mo):
    "Replace the entities that are specified by OpenID"
    return replacements.get(mo.group(1), mo.group())


def parseLinkAttrs(html, ignore_errors=False):
    """Find all link tags in a string representing a HTML document and
    return a list of their attributes.

    @param html: the text to parse
    @type html: str or unicode

    @param ignore_errors: whether to return despite e.g. parsing errors
    @type ignore_errors: bool

    @return: A list of dictionaries of attributes, one for each link tag
    @rtype: [[(type(html), type(html))]]
    """
    if isinstance(html, bytes):
        # Attempt to decode as UTF-8, since that's the most modern -- also
        # try Latin-1, since that's suggested by HTTP/1.1. If neither of
        # those works, fall over.
        try:
            html = html.decode("utf-8")
        except UnicodeDecodeError:
            try:
                html = html.decode("latin1")
            except UnicodeDecodeError:
                if ignore_errors:
                    # Optionally ignore the errors and act as if no link attrs
                    # were found here
                    return []
                else:
                    raise AssertionError("Unreadable HTML!")

    stripped = removeMarkup(html)
    html_mo = html_find.search(stripped)
    if html_mo is None or html_mo.start('contents') == -1:
        return []

    start, end = html_mo.span('contents')
    head_mo = head_find.search(stripped, start, end)
    if head_mo is None or head_mo.start('contents') == -1:
        return []

    start, end = head_mo.span('contents')
    link_mos = link_find.finditer(stripped, head_mo.start(), head_mo.end())

    matches = []
    for link_mo in link_mos:
        start = link_mo.start() + 5
        link_attrs = {}
        for attr_mo in attr_find.finditer(stripped, start):
            if attr_mo.lastgroup == 'end_link':
                break

            # Either q_val or unq_val must be present, but not both
            # unq_val is a True (non-empty) value if it is present
            attr_name, q_val, unq_val = attr_mo.group('attr_name', 'q_val',
                                                      'unq_val')
            attr_val = ent_replace.sub(replaceEnt, unq_val or q_val)

            link_attrs[attr_name] = attr_val

        matches.append(link_attrs)

    return matches


def relMatches(rel_attr, target_rel):
    """Does this target_rel appear in the rel_str?"""
    # XXX: TESTME
    rels = rel_attr.strip().split()
    for rel in rels:
        rel = rel.lower()
        if rel == target_rel:
            return 1

    return 0


def linkHasRel(link_attrs, target_rel):
    """Does this link have target_rel as a relationship?"""
    # XXX: TESTME
    rel_attr = link_attrs.get('rel')
    return rel_attr and relMatches(rel_attr, target_rel)


def findLinksRel(link_attrs_list, target_rel):
    """Filter the list of link attributes on whether it has target_rel
    as a relationship."""
    # XXX: TESTME
    matchesTarget = lambda attrs: linkHasRel(attrs, target_rel)
    return list(filter(matchesTarget, link_attrs_list))


def findFirstHref(link_attrs_list, target_rel):
    """Return the value of the href attribute for the first link tag
    in the list that has target_rel as a relationship."""
    # XXX: TESTME
    matches = findLinksRel(link_attrs_list, target_rel)
    if not matches:
        return None
    first = matches[0]
    return first.get('href')
