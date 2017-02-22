import unittest

from openid import codecutil  # registers encoder


class EncoderTest(unittest.TestCase):
    def test_handler_registered(self):
        self.assertEqual("foo".encode('ascii', errors='oid_percent_escape'),
                         b"foo")

    def test_encoding(self):
        s = 'l\xa1m\U00101010n'
        expected = b'l%C2%A1m%F4%81%80%90n'
        self.assertEqual(
            s.encode('ascii', errors='oid_percent_escape'), expected)


if __name__ == '__main__':
    unittest.main()
