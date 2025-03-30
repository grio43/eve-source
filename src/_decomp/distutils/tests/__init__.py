#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\__init__.py
import os
import sys
import unittest
here = os.path.dirname(__file__)

def test_suite():
    suite = unittest.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith('test') and fn.endswith('.py'):
            modname = 'distutils.tests.' + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(module.test_suite())

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
