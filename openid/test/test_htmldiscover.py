from openid.consumer.discover import OpenIDServiceEndpoint
from openid.test import datadriven


class BadLinksTestCase(datadriven.DataDrivenTestCase):
    cases = [
        '',
        "http://not.in.a.link.tag/",
        '<link rel="openid.server" href="not.in.html.or.head" />',
    ]

    def __init__(self, data):
        super(BadLinksTestCase, self).__init__(data)
        self.data = data

    def runOneTest(self):
        actual = OpenIDServiceEndpoint.fromHTML('http://unused.url/',
                                                self.data)
        expected = []
        self.assertEqual(expected, actual)


def pyUnitTests():
    return datadriven.loadTests(__name__)
