#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\jinja2\testsuite\__init__.py
import os
import re
import sys
import unittest
from traceback import format_exception
from jinja2 import loaders
here = os.path.dirname(os.path.abspath(__file__))
dict_loader = loaders.DictLoader({'justdict.html': 'FOO'})
package_loader = loaders.PackageLoader('jinja2.testsuite.res', 'templates')
filesystem_loader = loaders.FileSystemLoader(here + '/res/templates')
function_loader = loaders.FunctionLoader({'justfunction.html': 'FOO'}.get)
choice_loader = loaders.ChoiceLoader([dict_loader, package_loader])
prefix_loader = loaders.PrefixLoader({'a': filesystem_loader,
 'b': dict_loader})

class JinjaTestCase(unittest.TestCase):

    def setup(self):
        pass

    def teardown(self):
        pass

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def assert_equal(self, a, b):
        return self.assertEqual(a, b)

    def assert_raises(self, *args, **kwargs):
        return self.assertRaises(*args, **kwargs)

    def assert_traceback_matches(self, callback, expected_tb):
        try:
            callback()
        except Exception as e:
            tb = format_exception(*sys.exc_info())
            if re.search(expected_tb.strip(), ''.join(tb)) is None:
                raise self.fail('Traceback did not match:\n\n%s\nexpected:\n%s' % (''.join(tb), expected_tb))
        else:
            self.fail('Expected exception')


def suite():
    from jinja2.testsuite import ext, filters, tests, core_tags, loader, inheritance, imports, lexnparse, security, api, regression, debug, utils, doctests
    suite = unittest.TestSuite()
    suite.addTest(ext.suite())
    suite.addTest(filters.suite())
    suite.addTest(tests.suite())
    suite.addTest(core_tags.suite())
    suite.addTest(loader.suite())
    suite.addTest(inheritance.suite())
    suite.addTest(imports.suite())
    suite.addTest(lexnparse.suite())
    suite.addTest(security.suite())
    suite.addTest(api.suite())
    suite.addTest(regression.suite())
    suite.addTest(debug.suite())
    suite.addTest(utils.suite())
    if sys.version_info < (3, 0):
        suite.addTest(doctests.suite())
    return suite
