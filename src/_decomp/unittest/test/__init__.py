#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\unittest\test\__init__.py
import os
import sys
import unittest
here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def suite():
    suite = unittest.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith('test') and fn.endswith('.py'):
            modname = 'unittest.test.' + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
