import codecs


def _pct_escape_handler(err):
    '''
    Encoding error handler that does percent-escaping of Unicode, to be used
    with codecs.register_error
    '''
    chunk = err.object[err.start:err.end]
    encoded_octets = ("%%%X" % octet for octet in chunk.encode("utf-8"))
    return ("".join(encoded_octets), err.end)

codecs.register_error("percent_escape", _pct_escape_handler)
