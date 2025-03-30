#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_versionpredicate.py
import distutils.versionpredicate
import doctest

def test_suite():
    return doctest.DocTestSuite(distutils.versionpredicate)
