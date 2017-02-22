import os.path
from openid.dh import DiffieHellman, strxor


def test_strxor():
    NUL = b'\x00'

    cases = [
        (NUL, NUL, NUL),
        (b'\x01', NUL, b'\x01'),
        (b'a', b'a', NUL),
        (b'a', NUL, b'a'),
        (b'abc', NUL * 3, b'abc'),
        (b'x' * 10, NUL * 10, b'x' * 10),
        (b'\x01', b'\x02', b'\x03'),
        (b'\xf0', b'\x0f', b'\xff'),
        (b'\xff', b'\x0f', b'\xf0'),
    ]

    for aa, bb, expected in cases:
        actual = strxor(aa, bb)
        assert actual == expected, (aa, bb, expected, actual)

    exc_cases = [
        ('', 'a'),
        ('foo', 'ba'),
        (NUL * 3, NUL * 4),
        (''.join(map(chr, range(256))), ''.join(map(chr, range(128)))),
    ]

    for aa, bb in exc_cases:
        try:
            unexpected = strxor(aa, bb)
        except ValueError:
            pass
        else:
            assert False, 'Expected ValueError, got %r' % (unexpected, )


def test1():
    dh1 = DiffieHellman.fromDefaults()
    dh2 = DiffieHellman.fromDefaults()
    secret1 = dh1.getSharedSecret(dh2.public)
    secret2 = dh2.getSharedSecret(dh1.public)
    assert secret1 == secret2
    return secret1


def test_exchange():
    s1 = test1()
    s2 = test1()
    assert s1 != s2


def test_public():
    f = open(os.path.join(os.path.dirname(__file__), 'dhpriv'))
    dh = DiffieHellman.fromDefaults()
    try:
        for line in f:
            parts = line.strip().split(' ')
            dh._setPrivate(int(parts[0]))

            assert dh.public == int(parts[1])
    finally:
        f.close()


def test():
    test_exchange()
    test_public()
    test_strxor()


if __name__ == '__main__':
    test()
