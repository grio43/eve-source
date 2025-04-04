#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\testfixtures\tests\test_comparison.py
from testfixtures import Comparison as C, TempDirectory, compare
from testfixtures.compat import PY2, PY3, exception_module
from testfixtures.tests.sample1 import TestClassA, a_function
from unittest import TestCase
import sys
from .compat import py_33_plus, py_34_plus

class AClass:

    def __init__(self, x, y = None):
        self.x = x
        if y:
            self.y = y

    def __repr__(self):
        return '<' + self.__class__.__name__ + '>'


class BClass(AClass):
    pass


class WeirdException(Exception):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class X(object):
    __slots__ = ['x']

    def __repr__(self):
        return '<X>'


class FussyDefineComparison(object):

    def __init__(self, attr):
        self.attr = attr

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError()
        return False

    def __ne__(self, other):
        return not self == other


class TestC(TestCase):

    def test_example(self):
        r = a_function()
        self.assertEqual(r, (C('testfixtures.tests.sample1.TestClassA'), C('testfixtures.tests.sample1.TestClassB'), C('testfixtures.tests.sample1.TestClassA')))
        self.assertEqual(r[0].args[0], 1)
        self.assertEqual(r[1].args[0], 2)
        self.assertEqual(r[2].args[0], 3)

    def test_example_with_object(self):
        self.assertEqual(C(AClass(1, 2)), AClass(1, 2))
        self.assertNotEqual(AClass(1, 2), AClass(1, 2))

    def test_example_with_vars(self):
        self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, y=2), AClass(1, 2))

    def test_example_with_odd_vars(self):
        self.assertEqual(C('testfixtures.tests.test_comparison.AClass', {'x': 1,
         'y': 2}), AClass(1, 2))

    def test_example_not_strict(self):
        self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, strict=False), AClass(1, 2))

    def test_example_dont_use_c_wrappers_on_both_sides(self):
        e = ValueError('some message')
        try:
            self.assertEqual(C(e), C(e))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, ("<C(failed):{mod}.ValueError>wrong type</C> != \n  <C:{mod}.ValueError>\n  args:('some message',)\n  </C>".format(mod=exception_module),))
        else:
            self.fail('No exception raised!')

    def test_repr_module(self):
        self.assertEqual(repr(C('datetime')), '<C:datetime>')

    def test_repr_class(self):
        self.assertEqual(repr(C('testfixtures.tests.sample1.TestClassA')), '<C:testfixtures.tests.sample1.TestClassA>')

    def test_repr_function(self):
        self.assertEqual(repr(C('testfixtures.tests.sample1.z')), '<C:testfixtures.tests.sample1.z>')

    def test_repr_instance(self):
        self.assertEqual(repr(C(TestClassA('something'))), "\n  <C:testfixtures.tests.sample1.TestClassA>\n  args:('something',)\n  </C>")

    def test_repr_exception(self):
        self.assertEqual(repr(C(ValueError('something'))), "\n  <C:{0}.ValueError>\n  args:('something',)\n  </C>".format(exception_module))

    def test_repr_exception_not_args(self):
        r = repr(C(WeirdException(1, 2)))
        if sys.version_info >= (3, 2, 4):
            args = '  args:(1, 2)\n'
        else:
            args = '  args:()\n'
        self.assertEqual(r, '\n  <C:testfixtures.tests.test_comparison.WeirdException>\n' + args + '  x:1\n  y:2\n  </C>')

    def test_repr_class_and_vars(self):
        self.assertEqual(repr(C(TestClassA, {'args': (1,)})), '\n  <C:testfixtures.tests.sample1.TestClassA>\n  args:(1,)\n  </C>')

    def test_repr_nested(self):
        self.assertEqual(repr(C(TestClassA, y=C(AClass), z=C(BClass(1, 2)))), '\n  <C:testfixtures.tests.sample1.TestClassA>\n  y:<C:testfixtures.tests.test_comparison.AClass>\n  z:\n    <C:testfixtures.tests.test_comparison.BClass>\n    x:1\n    y:2\n    </C>\n  </C>')

    def test_repr_failed_wrong_class(self):
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, y=2), BClass(1, 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, ('<C(failed):testfixtures.tests.test_comparison.AClass>wrong type</C> != <BClass>',))
        else:
            self.fail('No exception raised!')

    def test_repr_failed_all_reasons_in_one(self):
        if py_34_plus:
            expected = ('\n  <C(failed):testfixtures.tests.test_com[79 chars] </C> != <AClass>',)
        else:
            expected = ("\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  x:1 not in Comparison\n  y:5 != 2\n  z:'missing' not in other\n  </C> != <AClass>",)
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', y=5, z='missing'), AClass(1, 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, expected)
        else:
            self.fail('No exception raised!')

    def test_repr_failed_not_in_other(self):
        if py_34_plus:
            expected = ('\n  <C(failed):testfixtures.tests.test_com[39 chars] </C> != <AClass>',)
        else:
            expected = ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  z:(3,) not in other\n  </C> != <AClass>',)
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, y=2, z=(3,)), AClass(1, 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, expected)
        else:
            self.fail('No exception raised!')

    def test_repr_failed_not_in_self_strict(self):
        if py_34_plus:
            expected = ('\n  <C(failed):testfixtures.tests.test_com[44 chars] </C> != <AClass>',)
        else:
            expected = ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  x:(1,) not in Comparison\n  </C> != <AClass>',)
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', y=2), AClass((1,), 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, expected)
        else:
            self.fail('No exception raised!')

    def test_repr_failed_not_in_self_not_strict(self):
        if py_34_plus:
            expected = ('\n  <C(failed):testfixtures.tests.test_com[39 chars] </C> != <AClass>',)
        else:
            expected = ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  z:(3,) not in other\n  </C> != <AClass>',)
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, y=2, z=(3,)), AClass(1, 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, expected)
        else:
            self.fail('No exception raised!')

    def test_repr_failed_one_attribute_not_equal(self):
        try:
            self.assertEqual(C('testfixtures.tests.test_comparison.AClass', x=1, y=(2,)), AClass(1, (3,)))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  y:(2,) != (3,)\n  </C> != <AClass>',))
        else:
            self.fail('No exception raised!')

    def test_repr_failed_nested(self):
        left_side = [C(AClass, x=1, y=2), C(BClass, x=C(AClass, x=1), y=C(AClass))]
        right_side = [AClass(1, 3), AClass(1, 3)]
        left_side == right_side
        self.assertEqual('[\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  y:2 != 3\n  </C>, \n  <C:testfixtures.tests.test_comparison.BClass>\n  x:\n    <C:testfixtures.tests.test_comparison.AClass>\n    x:1\n    </C>\n  y:<C:testfixtures.tests.test_comparison.AClass>\n  </C>]', repr(left_side))
        self.assertEqual('[<AClass>, <AClass>]', repr(right_side))

    def test_repr_failed_nested_failed(self):
        left_side = [C(AClass, x=1, y=2), C(BClass, x=C(AClass, x=1, strict=False), y=C(AClass, z=2))]
        right_side = [AClass(1, 2), BClass(AClass(1, 2), AClass(1, 2))]
        left_side == right_side
        self.assertEqual('[\n  <C:testfixtures.tests.test_comparison.AClass>\n  x:1\n  y:2\n  </C>, \n  <C(failed):testfixtures.tests.test_comparison.BClass>\n  y:\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  x:1 not in Comparison\n  y:2 not in Comparison\n  z:2 not in other\n  </C> != <AClass>\n  </C>]', repr(left_side))
        self.assertEqual('[<AClass>, <BClass>]', repr(right_side))

    def test_repr_failed_passed_failed(self):
        c = C('testfixtures.tests.test_comparison.AClass', x=1, y=2)
        try:
            self.assertEqual(c, AClass(1, 3))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  y:2 != 3\n  </C> != <AClass>',))
        else:
            self.fail('No exception raised!')

        self.assertEqual(c, AClass(1, 2))
        try:
            self.assertEqual(c, AClass(3, 2))
        except Exception as e:
            self.failUnless(isinstance(e, AssertionError))
            self.assertEqual(e.args, ('\n  <C(failed):testfixtures.tests.test_comparison.AClass>\n  x:1 != 3\n  </C> != <AClass>',))
        else:
            self.fail('No exception raised!')

    def test_first(self):
        self.assertEqual(C('testfixtures.tests.sample1.TestClassA'), TestClassA())

    def test_second(self):
        self.assertEqual(TestClassA(), C('testfixtures.tests.sample1.TestClassA'))

    def test_not_same_first(self):
        self.assertNotEqual(C('datetime'), TestClassA())

    def test_not_same_second(self):
        self.assertNotEqual(TestClassA(), C('datetime'))

    def test_object_supplied(self):
        self.assertEqual(TestClassA(1), C(TestClassA(1)))

    def test_class_and_vars(self):
        self.assertEqual(TestClassA(1), C(TestClassA, {'args': (1,)}))

    def test_class_and_kw(self):
        self.assertEqual(TestClassA(1), C(TestClassA, args=(1,)))

    def test_class_and_vars_and_kw(self):
        self.assertEqual(AClass(1, 2), C(AClass, {'x': 1}, y=2))

    def test_object_and_vars(self):
        self.assertEqual(TestClassA(1), C(TestClassA(), {'args': (1,)}))

    def test_object_and_kw(self):
        self.assertEqual(TestClassA(1), C(TestClassA(), args=(1,)))

    def test_object_not_strict(self):
        self.assertEqual(C(AClass(1), strict=False), AClass(1, 2))

    def test_exception(self):
        self.assertEqual(ValueError('foo'), C(ValueError('foo')))

    def test_exception_class_and_args(self):
        self.assertEqual(ValueError('foo'), C(ValueError, args=('foo',)))

    def test_exception_instance_and_args(self):
        self.assertEqual(ValueError('foo'), C(ValueError('bar'), args=('foo',)))

    def test_exception_not_same(self):
        self.assertNotEqual(ValueError('foo'), C(ValueError('bar')))

    def test_exception_no_args_different(self):
        self.assertNotEqual(WeirdException(1, 2), C(WeirdException(1, 3)))

    def test_exception_no_args_same(self):
        self.assertEqual(C(WeirdException(1, 2)), WeirdException(1, 2))

    def test_repr_file_different(self):
        with TempDirectory() as d:
            path = d.write('file', 'stuff')
            f = open(path)
            f.close()
        if PY3:
            c = C('io.TextIOWrapper', name=path, mode='r', closed=False, strict=False)
            self.assertNotEqual(f, c)
            compare(repr(c), '\n  <C(failed):_io.TextIOWrapper>\n  closed:False != True\n  </C>')
        else:
            c = C(file, name=path, mode='r', closed=False, strict=False)
            self.assertNotEqual(f, c)
            compare(repr(c), '\n  <C(failed):__builtin__.file>\n  closed:False != True\n  </C>')

    def test_file_same(self):
        with TempDirectory() as d:
            path = d.write('file', 'stuff')
            f = open(path)
            f.close()
        if PY3:
            self.assertEqual(f, C('io.TextIOWrapper', name=path, mode='r', closed=True, strict=False))
        else:
            self.assertEqual(f, C(file, name=path, mode='r', closed=True, strict=False))

    def test_no___dict___strict(self):
        x = X()
        try:
            self.assertEqual(C(X, x=1), x)
        except TypeError as e:
            self.assertEqual(e.args, ('<X> does not support vars() so cannot do strict comparison',))
        else:
            self.fail('No exception raised!')

    def test_no___dict___not_strict_same(self):
        x = X()
        x.x = 1
        self.assertEqual(C(X, x=1, strict=False), x)

    def test_no___dict___not_strict_different(self):
        if py_34_plus:
            expected = ('\n  <C(failed):testfixtures.tests.test_com[42 chars] </C> != <X>',)
        else:
            expected = ('\n  <C(failed):testfixtures.tests.test_comparison.X>\n  x:1 != 2\n  y:2 not in other\n  </C> != <X>',)
        x = X()
        x.x = 2
        try:
            self.assertEqual(C(X, x=1, y=2, strict=False), x)
        except AssertionError as e:
            compare(e.args, expected)
        else:
            self.fail('No exception raised!')

    def test_compared_object_defines_eq(self):

        class Annoying:

            def __init__(self):
                self.eq_called = 0

            def __eq__(self, other):
                self.eq_called += 1
                if isinstance(other, Annoying):
                    return True
                return False

        self.assertEqual(Annoying(), Annoying())
        self.assertFalse(Annoying() == C(Annoying))
        if PY2:
            self.assertFalse(Annoying() != C(Annoying))
        else:
            self.assertTrue(Annoying() != C(Annoying))
        self.assertTrue(C(Annoying) == Annoying())
        self.assertFalse(C(Annoying) != Annoying())
        c = C(Annoying, eq_called=1)
        c == Annoying()
        self.assertEqual(repr(c), '\n  <C(failed):testfixtures.tests.test_comparison.Annoying>\n  eq_called:1 != 0\n  </C>')

    def test_compared_object_class_attributes(self):

        class Classy(object):
            x = 1
            y = 2

        self.assertEqual(C(Classy, x=1, y=2), Classy())
        c = C(Classy, x=1, y=1)
        self.assertNotEqual(c, Classy())
        self.assertEqual(repr(c), '\n  <C(failed):testfixtures.tests.test_comparison.Classy>\n  y:1 != 2\n  </C>')
        ce = C(Classy, x=1, y=1)
        ca = Classy()
        ca.y = 1
        self.assertEqual(ce, ca)
        ce = C(Classy, x=1, y=2)
        ca = Classy()
        ca.y = 1
        self.assertNotEqual(ce, ca)
        self.assertEqual(repr(ce), '\n  <C(failed):testfixtures.tests.test_comparison.Classy>\n  y:2 != 1\n  </C>')

    def test_importerror(self):
        self.failIf(C(ImportError('x')) != ImportError('x'))

    def test_class_defines_comparison_strictly(self):
        self.assertEqual(C('testfixtures.tests.test_comparison.FussyDefineComparison', attr=1), FussyDefineComparison(1))

    def test_cant_resolve(self):
        try:
            C('testfixtures.bonkers')
        except Exception as e:
            self.failUnless(isinstance(e, AttributeError))
            self.assertEqual(e.args, ("'testfixtures.bonkers' could not be resolved",))
        else:
            self.fail('No exception raised!')

    def test_no_name(self):

        class NoName(object):
            pass

        NoName.__name__ = ''
        NoName.__module__ = ''
        c = C(NoName)
        if py_33_plus:
            expected = "<C:<class '.TestC.test_no_name.<locals>.NoName'>>"
        else:
            expected = "<C:<class '.'>>"
        self.assertEqual(repr(c), expected)
