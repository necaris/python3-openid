import unittest


class DataDrivenTestCase(unittest.TestCase):
    cases = []

    @classmethod
    def generateCases(cls):
        return cls.cases

    @classmethod
    def loadTests(cls):
        tests = []
        for case in cls.generateCases():
            if isinstance(case, tuple):
                test = cls(*case)
            elif isinstance(case, dict):
                test = cls(**case)
            else:
                test = cls(case)
            tests.append(test)
        return tests

    def __init__(self, description):
        super(DataDrivenTestCase, self).__init__(self, 'runOneTest')
        self.description = description

    def shortDescription(self):
        return '%s for %s' % (self.__class__.__name__, self.description)


def loadTests(module_name):
    loader = unittest.defaultTestLoader
    this_module = __import__(module_name, {}, {}, [None])

    tests = []
    for name in dir(this_module):
        obj = getattr(this_module, name)
        if isinstance(obj, unittest.TestCase):
            if hasattr(obj, 'loadTests'):
                tests.extend(obj.loadTests())
            else:
                tests.append(loader.loadTestsFromTestCase(obj))

    return unittest.TestSuite(tests)
