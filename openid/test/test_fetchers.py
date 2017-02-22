import warnings
import unittest
import urllib.request
import urllib.error
import urllib.parse

from openid import fetchers

# XXX: make these separate test cases


def _assertEqual(v1, v2, extra):
    try:
        assert v1 == v2
    except AssertionError:
        raise AssertionError("%r != %r ; context %r" % (v1, v2, extra))


def failUnlessResponseExpected(expected, actual, extra):
    _assertEqual(expected.final_url, actual.final_url, extra)
    _assertEqual(expected.status, actual.status, extra)
    _assertEqual(expected.body, actual.body, extra)
    got_headers = dict(actual.headers)

    del got_headers['date']
    del got_headers['server']

    for k, v in expected.headers.items():
        assert got_headers[k] == v, (k, v, got_headers[k], extra)


def test_fetcher(fetcher, should_raise_exc, server):
    def geturl(path):
        host, port = server.server_address
        return 'http://%s:%s%s' % (host, port, path)

    expected_headers = {'content-type': 'text/plain'}

    def plain(path, code):
        path = '/' + path
        expected = fetchers.HTTPResponse(
            geturl(path), code, expected_headers, path)
        return (path, expected)

    expect_success = fetchers.HTTPResponse(
        geturl('/success'), 200, expected_headers, '/success')
    cases = [
        ('/success', expect_success),
        ('/301redirect', expect_success),
        ('/302redirect', expect_success),
        ('/303redirect', expect_success),
        ('/307redirect', expect_success),
        plain('notfound', 404),
        plain('badreq', 400),
        plain('forbidden', 403),
        plain('error', 500),
        plain('server_error', 503),
    ]

    for path, expected in cases:
        fetch_url = geturl(path)
        try:
            actual = fetcher.fetch(fetch_url)
        except (SystemExit, KeyboardInterrupt):
            pass
        except Exception as e:
            raise AssertionError((fetcher, fetch_url, e))
        else:
            failUnlessResponseExpected(expected, actual, extra=locals())

    for err_url in [
            geturl('/closed'),
            'http://invalid.janrain.com/',
            'not:a/url',
            'ftp://janrain.com/pub/',
    ]:
        try:
            result = fetcher.fetch(err_url)
        except (KeyboardInterrupt, SystemExit):
            raise
        except fetchers.HTTPError:
            # This is raised by the Curl fetcher for bad cases
            # detected by the fetchers module, but it's a subclass of
            # HTTPFetchingError, so we have to catch it explicitly.
            assert should_raise_exc
        except fetchers.HTTPFetchingError:
            assert not should_raise_exc, (fetcher, should_raise_exc, server)
        except Exception as e:
            assert should_raise_exc
        else:
            assert False, 'An exception was expected for %r (%r)' % (fetcher,
                                                                     result)


def run_fetcher_tests(server):
    exc_fetchers = []
    for klass, library_name in [
        (fetchers.Urllib2Fetcher, 'urllib2'),
        (fetchers.CurlHTTPFetcher, 'pycurl'),
        (fetchers.HTTPLib2Fetcher, 'httplib2'),
    ]:
        try:
            exc_fetchers.append(klass())
        except RuntimeError as why:
            if str(why).startswith('Cannot find %s library' %
                                   (library_name, )):
                try:
                    __import__(library_name)
                except ImportError:
                    raise unittest.SkipTest(
                        'Skipping tests for %r fetcher because '
                        'the library did not import.' % (library_name, ))
                else:
                    assert False, ('%s present but not detected' %
                                   (library_name, ))
            else:
                raise

    non_exc_fetchers = []
    for f in exc_fetchers:
        non_exc_fetchers.append(fetchers.ExceptionWrappingFetcher(f))

    for f in exc_fetchers:
        test_fetcher(f, True, server)

    for f in non_exc_fetchers:
        test_fetcher(f, False, server)


from http.server import BaseHTTPRequestHandler, HTTPServer


class FetcherTestHandler(BaseHTTPRequestHandler):
    cases = {
        '/success': (200, None),
        '/301redirect': (301, '/success'),
        '/302redirect': (302, '/success'),
        '/303redirect': (303, '/success'),
        '/307redirect': (307, '/success'),
        '/notfound': (404, None),
        '/badreq': (400, None),
        '/forbidden': (403, None),
        '/error': (500, None),
        '/server_error': (503, None),
    }

    def log_request(self, *args):
        pass

    def do_GET(self):
        if self.path == '/closed':
            # *somehow* a ResourceWarning gets raised with an unclosed socket
            # when this is hit. It's virtually impossible to find out where.
            # Since ResourceWarnings are just warnings, ignore for now.
            pass
        else:
            try:
                http_code, location = self.cases[self.path]
            except KeyError:
                self.errorResponse('Bad path')
            else:
                extra_headers = [('Content-type', 'text/plain')]
                if location is not None:
                    host, port = self.server.server_address
                    base = ('http://%s:%s' % (host, port, ))
                    location = base + location
                    extra_headers.append(('Location', location))
                self._respond(http_code, extra_headers, self.path)

    def do_POST(self):
        try:
            http_code, extra_headers = self.cases[self.path]
        except KeyError:
            self.errorResponse('Bad path')
        else:
            if http_code in [301, 302, 303, 307]:
                self.errorResponse()
            else:
                content_type = self.headers.get('content-type', 'text/plain')
                extra_headers.append(('Content-type', content_type))
                content_length = int(self.headers.get('Content-length', '-1'))
                body = self.rfile.read(content_length)
                self._respond(http_code, extra_headers, body)

    def errorResponse(self, message=None):
        req = [
            ('HTTP method', self.command),
            ('path', self.path),
        ]
        if message:
            req.append(('message', message))

        body_parts = ['Bad request:\r\n']
        for k, v in req:
            body_parts.append(' %s: %s\r\n' % (k, v))
        body = ''.join(body_parts)
        self._respond(400, [('Content-type', 'text/plain')], body)

    def _respond(self, http_code, extra_headers, body):
        self.send_response(http_code)
        for k, v in extra_headers:
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(bytes(body, encoding="utf-8"))

    # def finish(self):
    #     if not self.wfile.closed:
    #         self.wfile.flush()
    #         # self.wfile.close()
    #     # self.rfile.close()


def test():
    host = 'localhost'
    # When I use port 0 here, it works for the first fetch and the
    # next one gets connection refused.  Bummer.  So instead, pick a
    # port that's *probably* not in use.
    import os
    port = (os.getpid() % 31000) + 1024

    server = HTTPServer((host, port), FetcherTestHandler)

    import threading
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    run_fetcher_tests(server)

    server.shutdown()


class FakeFetcher(object):
    sentinel = object()

    def fetch(self, *args, **kwargs):
        return self.sentinel


class DefaultFetcherTest(unittest.TestCase):
    def setUp(self):
        """reset the default fetcher to None"""
        fetchers.setDefaultFetcher(None)

    def tearDown(self):
        """reset the default fetcher to None"""
        fetchers.setDefaultFetcher(None)

    def test_getDefaultNotNone(self):
        """Make sure that None is never returned as a default fetcher"""
        self.assertTrue(fetchers.getDefaultFetcher() is not None)
        fetchers.setDefaultFetcher(None)
        self.assertTrue(fetchers.getDefaultFetcher() is not None)

    def test_setDefault(self):
        """Make sure the getDefaultFetcher returns the object set for
        setDefaultFetcher"""
        sentinel = object()
        fetchers.setDefaultFetcher(sentinel, wrap_exceptions=False)
        self.assertTrue(fetchers.getDefaultFetcher() is sentinel)

    def test_callFetch(self):
        """Make sure that fetchers.fetch() uses the default fetcher
        instance that was set."""
        fetchers.setDefaultFetcher(FakeFetcher())
        actual = fetchers.fetch('bad://url')
        self.assertTrue(actual is FakeFetcher.sentinel)

    def test_wrappedByDefault(self):
        """Make sure that the default fetcher instance wraps
        exceptions by default"""
        default_fetcher = fetchers.getDefaultFetcher()
        self.assertIsInstance(default_fetcher,
                              fetchers.ExceptionWrappingFetcher)

        self.assertRaises(fetchers.HTTPFetchingError, fetchers.fetch,
                          'http://invalid.janrain.com/')

    def test_notWrapped(self):
        """Make sure that if we set a non-wrapped fetcher as default,
        it will not wrap exceptions."""
        # A fetcher that will raise an exception when it encounters a
        # host that will not resolve
        fetcher = fetchers.Urllib2Fetcher()
        fetchers.setDefaultFetcher(fetcher, wrap_exceptions=False)

        self.assertFalse(
            isinstance(fetchers.getDefaultFetcher(),
                       fetchers.ExceptionWrappingFetcher))

        try:
            fetchers.fetch('http://invalid.janrain.com/')
        except fetchers.HTTPFetchingError:
            self.fail('Should not be wrapping exception')
        except Exception as exc:
            self.assertIsInstance(exc, urllib.error.URLError)
            pass
        else:
            self.fail('Should have raised an exception')


class Urllib2FetcherTests(unittest.TestCase):
    '''Make sure a few of the utility methods are also covered by tests.'''

    def setUp(self):
        self.fetcher = fetchers.Urllib2Fetcher()

    def test_disallowed(self):
        '''
        Test that the _allowedURL function only lets through the right things.
        '''
        for url in [
                "file://localhost/thing.txt", "ftp://server/path",
                "sftp://server/path", "ssh://server/path"
        ]:
            self.assertEqual(fetchers._allowedURL(url), False)

    def test_lowerCaseKeys(self):
        uppercased = {'Content-Type': None, 'HiPPyHiPPyShAKe': None}
        lowercased = {'content-type': None, 'hippyhippyshake': None}
        self.assertEqual(self.fetcher._lowerCaseKeys(uppercased), lowercased)

    def test_parseHeaderValue(self):
        headers_parsed = [
            ("text/html; charset=latin-1", ("text/html", {
                "charset": "latin-1"
            })),
            ("1; mode=block", ("1", {
                "mode": "block"
            })),
            ("foo; bar=baz; thing=quux", ("foo", {
                "bar": "baz",
                "thing": "quux"
            })),
        ]
        for s, p in headers_parsed:
            self.assertEqual(self.fetcher._parseHeaderValue(s), p)


def pyUnitTests():
    case1 = unittest.FunctionTestCase(test)
    loadTests = unittest.defaultTestLoader.loadTestsFromTestCase
    case2 = loadTests(DefaultFetcherTest)
    case3 = loadTests(Urllib2FetcherTests)
    return unittest.TestSuite([case1, case2, case3])
