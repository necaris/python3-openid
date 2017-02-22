import sys
import os.path
import warnings
import unittest


def addParentToPath():
    """
    Add the parent directory to sys.path to make it importable.
    """
    try:
        d = os.path.dirname(__file__)
    except NameError:
        d = os.path.dirname(sys.argv[0])
    parent = os.path.normpath(os.path.join(d, '..'))
    if parent not in sys.path:
        print("adding {} to sys.path".format(parent))
        sys.path.insert(0, parent)


def specialCaseTests():
    """
    Some modules have an explicit `test` function that collects tests --
    collect these together as a suite.
    """
    function_test_modules = [
        'cryptutil',
        'oidutil',
        'dh',
    ]

    suite = unittest.TestSuite()
    for module_name in function_test_modules:
        module_name = 'openid.test.' + module_name
        try:
            test_mod = __import__(module_name, {}, {}, [None])
        except ImportError:
            print(('Failed to import test %r' % (module_name, )))
        else:
            suite.addTest(unittest.FunctionTestCase(test_mod.test))

    return suite


def pyUnitTests():
    """
    Aggregate unit tests from modules, including a few special cases, and
    return a suite.
    """
    test_module_names = [
        'server',
        'consumer',
        'message',
        'symbol',
        'etxrd',
        'xri',
        'xrires',
        'association_response',
        'auth_request',
        'negotiation',
        'verifydisco',
        'sreg',
        'ax',
        'pape',
        'pape_draft2',
        'pape_draft5',
        'rpverify',
        'extension',
        'codecutil',
    ]

    test_modules = [
        __import__('openid.test.test_{}'.format(name), {}, {}, ['unused'])
        for name in test_module_names
    ]

    try:
        from openid.test import test_examples
    except ImportError:
        # This is very likely due to twill being unimportable, since it's
        # ancient and unmaintained. Until the examples are reimplemented using
        # something else, we just need to skip it
        warnings.warn("Could not import twill; skipping test_examples.")
    else:
        test_modules.append(test_examples)

    # Some modules have data-driven tests, and they use custom methods
    # to build the test suite -- the module-level pyUnitTests function should
    # return an appropriate test suite
    custom_module_names = [
        'kvform',
        'linkparse',
        'oidutil',
        'storetest',
        'test_accept',
        'test_association',
        'test_discover',
        'test_fetchers',
        'test_htmldiscover',
        'test_nonce',
        'test_openidyadis',
        'test_parsehtml',
        'test_urinorm',
        'test_yadis_discover',
        'trustroot',
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for m in test_modules:
        suite.addTest(loader.loadTestsFromModule(m))

    for name in custom_module_names:
        mod = __import__('openid.test.{}'.format(name), {}, {}, ['unused'])
        try:
            suite.addTest(mod.pyUnitTests())
        except AttributeError:
            # because the AttributeError doesn't actually say which
            # object it was.
            print(("Error loading tests from %s:" % (name, )))
            raise

    return suite


def _import_djopenid():
    """
    Import djopenid from the examples directory without putting it in sys.path
    permanently (which we don't really want to do as we don't want namespace
    conflicts)
    """
    # Find our way to the examples/djopenid directory
    grandParentDir = os.path.join(__file__, "..", "..", "..")
    grandParentDir = os.path.abspath(grandParentDir)
    examplesDir = os.path.join(grandParentDir, "examples")

    sys.path.append(examplesDir)
    import djopenid
    sys.path.remove(examplesDir)


def djangoExampleTests():
    """
    Run tests from examples/djopenid.

    @return: number of failed tests.
    """
    # Django uses this to find out where its settings are.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'djopenid.settings'

    _import_djopenid()

    try:
        import django.test.simple
    except ImportError:
        raise unittest.SkipTest("Skipping django examples. "
                                "django.test.simple not found.")

    import djopenid.server.models
    import djopenid.consumer.models
    print("Testing Django examples:")

    runner = django.test.simple.DjangoTestSuiteRunner()
    return runner.run_tests(['server', 'consumer'])

    # These tests do get put into a test suite, so we could run them with the
    # other tests, but django also establishes a test database for them, so we
    # let it do that thing instead.
    return django.test.simple.run_tests(
        [djopenid.server.models, djopenid.consumer.models])


def test_suite():
    """
    Collect all of the tests together in a single suite.
    """
    addParentToPath()
    combined_suite = unittest.TestSuite()
    combined_suite.addTests(specialCaseTests())
    combined_suite.addTests(pyUnitTests())
    combined_suite.addTest(unittest.FunctionTestCase(djangoExampleTests))
    return combined_suite
