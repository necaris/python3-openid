import unittest
import string
import time
import os
import uuid

try:
    import psycopg2
except ImportError:
    from psycopg2cffi import compat

    compat.register()

from openid.association import Association
from openid.cryptutil import randomString
from openid.store.nonce import mkNonce, split

allowed_handle = []
for c in string.printable:
    if c not in string.whitespace:
        allowed_handle.append(c)
allowed_handle = "".join(allowed_handle)


def generateHandle(n):
    return randomString(n, allowed_handle)


generateSecret = randomString


def getTmpDbName():
    """Returns a name suitable for creating a temporary database.

    Restrictions:
     - Maximum length 64 characters (MySQL)
    """
    return "openid_test_%s" % uuid.uuid4().hex


def testStore(store):
    """Make sure a given store has a minimum of API compliance. Call
    this function with an empty store.

    Raises AssertionError if the store does not work as expected.

    OpenIDStore -> NoneType
    """
    ### Association functions
    now = int(time.time())

    server_url = "http://www.myopenid.com/openid"

    def genAssoc(issued, lifetime=600):
        sec = generateSecret(20)
        hdl = generateHandle(128)
        return Association(hdl, sec, now + issued, lifetime, "HMAC-SHA1")

    def checkRetrieve(url, handle=None, expected=None):
        retrieved_assoc = store.getAssociation(url, handle)
        assert retrieved_assoc == expected, (
            retrieved_assoc.__dict__,
            expected.__dict__,
        )
        if expected is not None:
            if retrieved_assoc is expected:
                print(
                    "Unexpected: retrieved a reference to the expected "
                    "value instead of a new object"
                )
            assert retrieved_assoc.handle == expected.handle
            assert retrieved_assoc.secret == expected.secret

    def checkRemove(url, handle, expected):
        present = store.removeAssociation(url, handle)
        assert bool(expected) == bool(present)

    assoc = genAssoc(issued=0)

    # Make sure that a missing association returns no result
    checkRetrieve(server_url)

    # Check that after storage, getting returns the same result
    store.storeAssociation(server_url, assoc)
    checkRetrieve(server_url, None, assoc)

    # more than once
    checkRetrieve(server_url, None, assoc)

    # Storing more than once has no ill effect
    store.storeAssociation(server_url, assoc)
    checkRetrieve(server_url, None, assoc)

    # Removing an association that does not exist returns not present
    checkRemove(server_url, assoc.handle + "x", False)

    # Removing an association that does not exist returns not present
    checkRemove(server_url + "x", assoc.handle, False)

    # Removing an association that is present returns present
    checkRemove(server_url, assoc.handle, True)

    # but not present on subsequent calls
    checkRemove(server_url, assoc.handle, False)

    # Put assoc back in the store
    store.storeAssociation(server_url, assoc)

    # More recent and expires after assoc
    assoc2 = genAssoc(issued=1)
    store.storeAssociation(server_url, assoc2)

    # After storing an association with a different handle, but the
    # same server_url, the handle with the later issue date is returned.
    checkRetrieve(server_url, None, assoc2)

    # We can still retrieve the older association
    checkRetrieve(server_url, assoc.handle, assoc)

    # Plus we can retrieve the association with the later issue date
    # explicitly
    checkRetrieve(server_url, assoc2.handle, assoc2)

    # More recent, and expires earlier than assoc2 or assoc. Make sure
    # that we're picking the one with the latest issued date and not
    # taking into account the expiration.
    assoc3 = genAssoc(issued=2, lifetime=100)
    store.storeAssociation(server_url, assoc3)

    checkRetrieve(server_url, None, assoc3)
    checkRetrieve(server_url, assoc.handle, assoc)
    checkRetrieve(server_url, assoc2.handle, assoc2)
    checkRetrieve(server_url, assoc3.handle, assoc3)

    checkRemove(server_url, assoc2.handle, True)

    checkRetrieve(server_url, None, assoc3)
    checkRetrieve(server_url, assoc.handle, assoc)
    checkRetrieve(server_url, assoc2.handle, None)
    checkRetrieve(server_url, assoc3.handle, assoc3)

    checkRemove(server_url, assoc2.handle, False)
    checkRemove(server_url, assoc3.handle, True)

    checkRetrieve(server_url, None, assoc)
    checkRetrieve(server_url, assoc.handle, assoc)
    checkRetrieve(server_url, assoc2.handle, None)
    checkRetrieve(server_url, assoc3.handle, None)

    checkRemove(server_url, assoc2.handle, False)
    checkRemove(server_url, assoc.handle, True)
    checkRemove(server_url, assoc3.handle, False)

    checkRetrieve(server_url, None, None)
    checkRetrieve(server_url, assoc.handle, None)
    checkRetrieve(server_url, assoc2.handle, None)
    checkRetrieve(server_url, assoc3.handle, None)

    checkRemove(server_url, assoc2.handle, False)
    checkRemove(server_url, assoc.handle, False)
    checkRemove(server_url, assoc3.handle, False)

    ### test expired associations
    # assoc 1: server 1, valid
    # assoc 2: server 1, expired
    # assoc 3: server 2, expired
    # assoc 4: server 3, valid
    assocValid1 = genAssoc(issued=-3600, lifetime=7200)
    assocValid2 = genAssoc(issued=-5)
    assocExpired1 = genAssoc(issued=-7200, lifetime=3600)
    assocExpired2 = genAssoc(issued=-7200, lifetime=3600)

    store.cleanupAssociations()
    store.storeAssociation(server_url + "1", assocValid1)
    store.storeAssociation(server_url + "1", assocExpired1)
    store.storeAssociation(server_url + "2", assocExpired2)
    store.storeAssociation(server_url + "3", assocValid2)

    cleaned = store.cleanupAssociations()
    assert cleaned == 2, cleaned

    ### Nonce functions

    def checkUseNonce(nonce, expected, server_url, msg=""):
        stamp, salt = split(nonce)
        actual = store.useNonce(server_url, stamp, salt)
        assert bool(actual) == bool(expected), "%r != %r: %s" % (actual, expected, msg)

    for url in [server_url, ""]:
        # Random nonce (not in store)
        nonce1 = mkNonce()

        # A nonce is allowed by default
        checkUseNonce(nonce1, True, url)

        # Storing once causes useNonce to return True the first, and only
        # the first, time it is called after the store.
        checkUseNonce(nonce1, False, url)
        checkUseNonce(nonce1, False, url)

        # Nonces from when the universe was an hour old should not pass now.
        old_nonce = mkNonce(3600)
        checkUseNonce(old_nonce, False, url, "Old nonce (%r) passed." % (old_nonce,))

    old_nonce1 = mkNonce(now - 20000)
    old_nonce2 = mkNonce(now - 10000)
    recent_nonce = mkNonce(now - 600)

    from openid.store import nonce as nonceModule

    orig_skew = nonceModule.SKEW
    try:
        nonceModule.SKEW = 0
        store.cleanupNonces()
        # Set SKEW high so stores will keep our nonces.
        nonceModule.SKEW = 100000
        assert store.useNonce(server_url, *split(old_nonce1))
        assert store.useNonce(server_url, *split(old_nonce2))
        assert store.useNonce(server_url, *split(recent_nonce))

        nonceModule.SKEW = 3600
        cleaned = store.cleanupNonces()
        assert cleaned == 2, "Cleaned %r nonces." % (cleaned,)

        nonceModule.SKEW = 100000
        # A roundabout method of checking that the old nonces were cleaned is
        # to see if we're allowed to add them again.
        assert store.useNonce(server_url, *split(old_nonce1))
        assert store.useNonce(server_url, *split(old_nonce2))
        # The recent nonce wasn't cleaned, so it should still fail.
        assert not store.useNonce(server_url, *split(recent_nonce))
    finally:
        nonceModule.SKEW = orig_skew


def test_filestore():
    from openid.store import filestore
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    store = filestore.FileOpenIDStore(temp_dir)

    testStore(store)
    store.cleanup()
    shutil.rmtree(temp_dir)


def test_sqlite():
    from openid.store import sqlstore
    import sqlite3

    conn = sqlite3.connect(":memory:")
    store = sqlstore.SQLiteStore(conn)
    store.createTables()
    testStore(store)


def test_mysql():
    from openid.store import sqlstore

    try:
        import MySQLdb
    except ImportError:
        raise unittest.SkipTest(
            "Skipping MySQL store tests. " "Could not import MySQLdb."
        )

    else:
        db_host = os.environ.get("TEST_MYSQL_HOST", "localhost")
        db_user = os.environ.get("TEST_MYSQL_USER", "openid_test")
        db_passwd = os.environ.get("TEST_MYSQL_PASSWORD", "password")
        db_name = getTmpDbName()

        from MySQLdb.constants import ER

        # Change this connect line to use the right user and password
        try:
            conn = MySQLdb.connect(user=db_user, passwd=db_passwd, host=db_host)
        except MySQLdb.OperationalError as why:
            if why.args[0] == 2005:
                raise unittest.SkipTest(
                    "Skipping MySQL store test. "
                    "Cannot connect to server on host %r." % (db_host,)
                )
            else:
                raise

        conn.query("CREATE DATABASE %s;" % db_name)
        try:
            conn.query("USE %s;" % db_name)

            # OK, we're in the right environment. Create store and
            # create the tables.
            store = sqlstore.MySQLStore(conn)
            store.createTables()

            # At last, we get to run the test.
            testStore(store)
        finally:
            # Remove the database. If you want to do post-mortem on a
            # failing test, comment out this line.
            conn.query("DROP DATABASE %s;" % db_name)


def test_postgresql():
    """
    Tests the PostgreSQLStore on a locally-hosted PostgreSQL database
    cluster, version 7.4 or later.  To run this test, you must have:

    - The 'psycopg2' python module (version 1.1) installed

    - PostgreSQL running locally

    - An 'openid_test' user account in your database cluster, which
      you can create by running 'createuser -Ad openid_test' as the
      'postgres' user

    - Trust auth for the 'openid_test' account, which you can activate
      by adding the following line to your pg_hba.conf file:

      local all openid_test trust

    This test connects to the database cluster three times:

    - To the 'template1' database, to create the test database

    - To the test database, to run the store tests

    - To the 'template1' database once more, to drop the test database
    """
    from openid.store import sqlstore

    try:
        import psycopg2
    except ImportError:
        raise unittest.SkipTest(
            "Skipping PostgreSQL store tests. " "Could not import psycopg2."
        )
    else:
        db_name = getTmpDbName()
        db_host = os.environ.get("TEST_POSTGRES_HOST", "localhost")
        db_user = os.environ.get("TEST_POSTGRES_USER", "openid_test")
        db_passwd = os.environ.get("TEST_POSTGRES_PASSWORD", "password")

        # Connect once to create the database; reconnect to access the
        # new database.
        try:
            conn_create = psycopg2.connect(
                database="template1", user=db_user, host=db_host, password=db_passwd
            )
        except psycopg2.OperationalError as why:
            raise unittest.SkipTest("Skipping PostgreSQL store test: %s" % why)

        conn_create.autocommit = True

        # Create the test database.
        cursor = conn_create.cursor()
        cursor.execute("CREATE DATABASE %s;" % (db_name,))
        conn_create.close()

        # Connect to the test database.
        conn_test = psycopg2.connect(database=db_name, user=db_user, host=db_host)

        # OK, we're in the right environment. Create the store
        # instance and create the tables.
        store = sqlstore.PostgreSQLStore(conn_test)
        store.createTables()

        # At last, we get to run the test.
        testStore(store)

        # Disconnect.
        conn_test.close()

        # It takes a little time for the close() call above to take
        # effect, so we'll wait for a second before trying to remove
        # the database.  (Maybe this is because we're using a UNIX
        # socket to connect to postgres rather than TCP?)
        import time

        time.sleep(1)

        # Remove the database now that the test is over.
        conn_remove = psycopg2.connect(database="template1", user=db_user, host=db_host)
        conn_remove.autocommit = True

        cursor = conn_remove.cursor()
        cursor.execute("DROP DATABASE %s;" % (db_name,))
        conn_remove.close()


def test_memstore():
    from openid.store import memstore

    testStore(memstore.MemoryStore())


test_functions = [
    test_filestore,
    test_sqlite,
    test_mysql,
    test_postgresql,
    test_memstore,
]


def pyUnitTests():
    tests = list(map(unittest.FunctionTestCase, test_functions))
    return unittest.TestSuite(tests)


if __name__ == "__main__":
    import sys

    suite = pyUnitTests()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
