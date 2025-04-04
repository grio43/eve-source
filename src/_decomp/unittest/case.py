#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\unittest\case.py
import sys
import functools
import difflib
import pprint
import re
import warnings
from . import result
from .util import strclass, safe_repr, sorted_list_difference, unorderable_list_difference
__unittest = True
DIFF_OMITTED = '\nDiff is %s characters long. Set self.maxDiff to None to see it.'

class SkipTest(Exception):
    pass


class _ExpectedFailure(Exception):

    def __init__(self, exc_info):
        super(_ExpectedFailure, self).__init__()
        self.exc_info = exc_info


class _UnexpectedSuccess(Exception):
    pass


def _id(obj):
    return obj


def skip(reason):

    def decorator(test_item):
        if not (isinstance(test_item, type) and issubclass(test_item, TestCase)):

            @functools.wraps(test_item)
            def skip_wrapper(*args, **kwargs):
                raise SkipTest(reason)

            test_item = skip_wrapper
        test_item.__unittest_skip__ = True
        test_item.__unittest_skip_why__ = reason
        return test_item

    return decorator


def skipIf(condition, reason):
    if condition:
        return skip(reason)
    return _id


def skipUnless(condition, reason):
    if not condition:
        return skip(reason)
    return _id


def expectedFailure(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise _ExpectedFailure(sys.exc_info())

        raise _UnexpectedSuccess

    return wrapper


class _AssertRaisesContext(object):

    def __init__(self, expected, test_case, expected_regexp = None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)

            raise self.failureException('{0} not raised'.format(exc_name))
        if not issubclass(exc_type, self.expected):
            return False
        self.exception = exc_value
        if self.expected_regexp is None:
            return True
        expected_regexp = self.expected_regexp
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' % (expected_regexp.pattern, str(exc_value)))
        return True


class TestCase(object):
    failureException = AssertionError
    longMessage = False
    maxDiff = 640
    _classSetupFailed = False

    def __init__(self, methodName = 'runTest'):
        self._testMethodName = methodName
        self._resultForDoCleanups = None
        try:
            testMethod = getattr(self, methodName)
        except AttributeError:
            raise ValueError('no such test method in %s: %s' % (self.__class__, methodName))

        self._testMethodDoc = testMethod.__doc__
        self._cleanups = []
        self._type_equality_funcs = {}
        self.addTypeEqualityFunc(dict, self.assertDictEqual)
        self.addTypeEqualityFunc(list, self.assertListEqual)
        self.addTypeEqualityFunc(tuple, self.assertTupleEqual)
        self.addTypeEqualityFunc(set, self.assertSetEqual)
        self.addTypeEqualityFunc(frozenset, self.assertSetEqual)
        self.addTypeEqualityFunc(unicode, self.assertMultiLineEqual)

    def addTypeEqualityFunc(self, typeobj, function):
        self._type_equality_funcs[typeobj] = function

    def addCleanup(self, function, *args, **kwargs):
        self._cleanups.append((function, args, kwargs))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def countTestCases(self):
        return 1

    def defaultTestResult(self):
        return result.TestResult()

    def shortDescription(self):
        doc = self._testMethodDoc
        return doc and doc.split('\n')[0].strip() or None

    def id(self):
        return '%s.%s' % (strclass(self.__class__), self._testMethodName)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._testMethodName == other._testMethodName

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((type(self), self._testMethodName))

    def __str__(self):
        return '%s (%s)' % (self._testMethodName, strclass(self.__class__))

    def __repr__(self):
        return '<%s testMethod=%s>' % (strclass(self.__class__), self._testMethodName)

    def _addSkip(self, result, reason):
        addSkip = getattr(result, 'addSkip', None)
        if addSkip is not None:
            addSkip(self, reason)
        else:
            warnings.warn('TestResult has no addSkip method, skips not reported', RuntimeWarning, 2)
            result.addSuccess(self)

    def run(self, result = None):
        orig_result = result
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
        self._resultForDoCleanups = result
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        if getattr(self.__class__, '__unittest_skip__', False) or getattr(testMethod, '__unittest_skip__', False):
            try:
                skip_why = getattr(self.__class__, '__unittest_skip_why__', '') or getattr(testMethod, '__unittest_skip_why__', '')
                self._addSkip(result, skip_why)
            finally:
                result.stopTest(self)

            return
        try:
            success = False
            try:
                self.setUp()
            except SkipTest as e:
                self._addSkip(result, str(e))
            except Exception:
                result.addError(self, sys.exc_info())
            else:
                try:
                    testMethod()
                except self.failureException:
                    result.addFailure(self, sys.exc_info())
                except _ExpectedFailure as e:
                    addExpectedFailure = getattr(result, 'addExpectedFailure', None)
                    if addExpectedFailure is not None:
                        addExpectedFailure(self, e.exc_info)
                    else:
                        warnings.warn('TestResult has no addExpectedFailure method, reporting as passes', RuntimeWarning)
                        result.addSuccess(self)
                except _UnexpectedSuccess:
                    addUnexpectedSuccess = getattr(result, 'addUnexpectedSuccess', None)
                    if addUnexpectedSuccess is not None:
                        addUnexpectedSuccess(self)
                    else:
                        warnings.warn('TestResult has no addUnexpectedSuccess method, reporting as failures', RuntimeWarning)
                        result.addFailure(self, sys.exc_info())
                except SkipTest as e:
                    self._addSkip(result, str(e))
                except Exception:
                    result.addError(self, sys.exc_info())
                else:
                    success = True

                try:
                    self.tearDown()
                except Exception:
                    result.addError(self, sys.exc_info())
                    success = False

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)
        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

    def doCleanups(self):
        result = self._resultForDoCleanups
        ok = True
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop(-1)
            try:
                function(*args, **kwargs)
            except Exception:
                ok = False
                result.addError(self, sys.exc_info())

        return ok

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def debug(self):
        self.setUp()
        getattr(self, self._testMethodName)()
        self.tearDown()
        while self._cleanups:
            function, args, kwargs = self._cleanups.pop(-1)
            function(*args, **kwargs)

    def skipTest(self, reason):
        raise SkipTest(reason)

    def fail(self, msg = None):
        raise self.failureException(msg)

    def assertFalse(self, expr, msg = None):
        if expr:
            msg = self._formatMessage(msg, '%s is not False' % safe_repr(expr))
            raise self.failureException(msg)

    def assertTrue(self, expr, msg = None):
        if not expr:
            msg = self._formatMessage(msg, '%s is not True' % safe_repr(expr))
            raise self.failureException(msg)

    def _formatMessage(self, msg, standardMsg):
        if not self.longMessage:
            return msg or standardMsg
        if msg is None:
            return standardMsg
        try:
            return '%s : %s' % (standardMsg, msg)
        except UnicodeDecodeError:
            return '%s : %s' % (safe_repr(standardMsg), safe_repr(msg))

    def assertRaises(self, excClass, callableObj = None, *args, **kwargs):
        context = _AssertRaisesContext(excClass, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    def _getAssertEqualityFunc(self, first, second):
        if type(first) is type(second):
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None:
                return asserter
        return self._baseAssertEqual

    def _baseAssertEqual(self, first, second, msg = None):
        if not first == second:
            standardMsg = '%s != %s' % (safe_repr(first), safe_repr(second))
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)

    def assertEqual(self, first, second, msg = None):
        assertion_func = self._getAssertEqualityFunc(first, second)
        assertion_func(first, second, msg=msg)

    def assertNotEqual(self, first, second, msg = None):
        if not first != second:
            msg = self._formatMessage(msg, '%s == %s' % (safe_repr(first), safe_repr(second)))
            raise self.failureException(msg)

    def assertAlmostEqual(self, first, second, places = None, msg = None, delta = None):
        if first == second:
            return
        if delta is not None and places is not None:
            raise TypeError('specify delta or places not both')
        if delta is not None:
            if abs(first - second) <= delta:
                return
            standardMsg = '%s != %s within %s delta' % (safe_repr(first), safe_repr(second), safe_repr(delta))
        else:
            if places is None:
                places = 7
            if round(abs(second - first), places) == 0:
                return
            standardMsg = '%s != %s within %r places' % (safe_repr(first), safe_repr(second), places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def assertNotAlmostEqual(self, first, second, places = None, msg = None, delta = None):
        if delta is not None and places is not None:
            raise TypeError('specify delta or places not both')
        if delta is not None:
            if not first == second and abs(first - second) > delta:
                return
            standardMsg = '%s == %s within %s delta' % (safe_repr(first), safe_repr(second), safe_repr(delta))
        else:
            if places is None:
                places = 7
            if not first == second and round(abs(second - first), places) != 0:
                return
            standardMsg = '%s == %s within %r places' % (safe_repr(first), safe_repr(second), places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    assertEquals = assertEqual
    assertNotEquals = assertNotEqual
    assertAlmostEquals = assertAlmostEqual
    assertNotAlmostEquals = assertNotAlmostEqual
    assert_ = assertTrue

    def _deprecate(original_func):

        def deprecated_func(*args, **kwargs):
            warnings.warn('Please use {0} instead.'.format(original_func.__name__), PendingDeprecationWarning, 2)
            return original_func(*args, **kwargs)

        return deprecated_func

    failUnlessEqual = _deprecate(assertEqual)
    failIfEqual = _deprecate(assertNotEqual)
    failUnlessAlmostEqual = _deprecate(assertAlmostEqual)
    failIfAlmostEqual = _deprecate(assertNotAlmostEqual)
    failUnless = _deprecate(assertTrue)
    failUnlessRaises = _deprecate(assertRaises)
    failIf = _deprecate(assertFalse)

    def assertSequenceEqual(self, seq1, seq2, msg = None, seq_type = None):
        if seq_type is not None:
            seq_type_name = seq_type.__name__
            if not isinstance(seq1, seq_type):
                raise self.failureException('First sequence is not a %s: %s' % (seq_type_name, safe_repr(seq1)))
            if not isinstance(seq2, seq_type):
                raise self.failureException('Second sequence is not a %s: %s' % (seq_type_name, safe_repr(seq2)))
        else:
            seq_type_name = 'sequence'
        differing = None
        try:
            len1 = len(seq1)
        except (TypeError, NotImplementedError):
            differing = 'First %s has no length.    Non-sequence?' % seq_type_name

        if differing is None:
            try:
                len2 = len(seq2)
            except (TypeError, NotImplementedError):
                differing = 'Second %s has no length.    Non-sequence?' % seq_type_name

        if differing is None:
            if seq1 == seq2:
                return
            seq1_repr = safe_repr(seq1)
            seq2_repr = safe_repr(seq2)
            if len(seq1_repr) > 30:
                seq1_repr = seq1_repr[:30] + '...'
            if len(seq2_repr) > 30:
                seq2_repr = seq2_repr[:30] + '...'
            elements = (seq_type_name.capitalize(), seq1_repr, seq2_repr)
            differing = '%ss differ: %s != %s\n' % elements
            for i in xrange(min(len1, len2)):
                try:
                    item1 = seq1[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += '\nUnable to index element %d of first %s\n' % (i, seq_type_name)
                    break

                try:
                    item2 = seq2[i]
                except (TypeError, IndexError, NotImplementedError):
                    differing += '\nUnable to index element %d of second %s\n' % (i, seq_type_name)
                    break

                if item1 != item2:
                    differing += '\nFirst differing element %d:\n%s\n%s\n' % (i, item1, item2)
                    break
            else:
                if len1 == len2 and seq_type is None and type(seq1) != type(seq2):
                    return

            if len1 > len2:
                differing += '\nFirst %s contains %d additional elements.\n' % (seq_type_name, len1 - len2)
                try:
                    differing += 'First extra element %d:\n%s\n' % (len2, seq1[len2])
                except (TypeError, IndexError, NotImplementedError):
                    differing += 'Unable to index element %d of first %s\n' % (len2, seq_type_name)

            elif len1 < len2:
                differing += '\nSecond %s contains %d additional elements.\n' % (seq_type_name, len2 - len1)
                try:
                    differing += 'First extra element %d:\n%s\n' % (len1, seq2[len1])
                except (TypeError, IndexError, NotImplementedError):
                    differing += 'Unable to index element %d of second %s\n' % (len1, seq_type_name)

        standardMsg = differing
        diffMsg = '\n' + '\n'.join(difflib.ndiff(pprint.pformat(seq1).splitlines(), pprint.pformat(seq2).splitlines()))
        standardMsg = self._truncateMessage(standardMsg, diffMsg)
        msg = self._formatMessage(msg, standardMsg)
        self.fail(msg)

    def _truncateMessage(self, message, diff):
        max_diff = self.maxDiff
        if max_diff is None or len(diff) <= max_diff:
            return message + diff
        return message + DIFF_OMITTED % len(diff)

    def assertListEqual(self, list1, list2, msg = None):
        self.assertSequenceEqual(list1, list2, msg, seq_type=list)

    def assertTupleEqual(self, tuple1, tuple2, msg = None):
        self.assertSequenceEqual(tuple1, tuple2, msg, seq_type=tuple)

    def assertSetEqual(self, set1, set2, msg = None):
        try:
            difference1 = set1.difference(set2)
        except TypeError as e:
            self.fail('invalid type when attempting set difference: %s' % e)
        except AttributeError as e:
            self.fail('first argument does not support set difference: %s' % e)

        try:
            difference2 = set2.difference(set1)
        except TypeError as e:
            self.fail('invalid type when attempting set difference: %s' % e)
        except AttributeError as e:
            self.fail('second argument does not support set difference: %s' % e)

        if not (difference1 or difference2):
            return
        lines = []
        if difference1:
            lines.append('Items in the first set but not the second:')
            for item in difference1:
                lines.append(repr(item))

        if difference2:
            lines.append('Items in the second set but not the first:')
            for item in difference2:
                lines.append(repr(item))

        standardMsg = '\n'.join(lines)
        self.fail(self._formatMessage(msg, standardMsg))

    def assertIn(self, member, container, msg = None):
        if member not in container:
            standardMsg = '%s not found in %s' % (safe_repr(member), safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIn(self, member, container, msg = None):
        if member in container:
            standardMsg = '%s unexpectedly found in %s' % (safe_repr(member), safe_repr(container))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIs(self, expr1, expr2, msg = None):
        if expr1 is not expr2:
            standardMsg = '%s is not %s' % (safe_repr(expr1), safe_repr(expr2))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNot(self, expr1, expr2, msg = None):
        if expr1 is expr2:
            standardMsg = 'unexpectedly identical: %s' % (safe_repr(expr1),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictEqual(self, d1, d2, msg = None):
        self.assertIsInstance(d1, dict, 'First argument is not a dictionary')
        self.assertIsInstance(d2, dict, 'Second argument is not a dictionary')
        if d1 != d2:
            standardMsg = '%s != %s' % (safe_repr(d1, True), safe_repr(d2, True))
            diff = '\n' + '\n'.join(difflib.ndiff(pprint.pformat(d1).splitlines(), pprint.pformat(d2).splitlines()))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDictContainsSubset(self, expected, actual, msg = None):
        missing = []
        mismatched = []
        for key, value in expected.iteritems():
            if key not in actual:
                missing.append(key)
            elif value != actual[key]:
                mismatched.append('%s, expected: %s, actual: %s' % (safe_repr(key), safe_repr(value), safe_repr(actual[key])))

        if not (missing or mismatched):
            return
        standardMsg = ''
        if missing:
            standardMsg = 'Missing: %s' % ','.join((safe_repr(m) for m in missing))
        if mismatched:
            if standardMsg:
                standardMsg += '; '
            standardMsg += 'Mismatched values: %s' % ','.join(mismatched)
        self.fail(self._formatMessage(msg, standardMsg))

    def assertItemsEqual(self, expected_seq, actual_seq, msg = None):
        with warnings.catch_warnings():
            if sys.py3kwarning:
                for _msg in ['(code|dict|type) inequality comparisons', 'builtin_function_or_method order comparisons', 'comparing unequal types']:
                    warnings.filterwarnings('ignore', _msg, DeprecationWarning)

            try:
                expected = sorted(expected_seq)
                actual = sorted(actual_seq)
            except TypeError:
                expected = list(expected_seq)
                actual = list(actual_seq)
                missing, unexpected = unorderable_list_difference(expected, actual, ignore_duplicate=False)
            else:
                return self.assertSequenceEqual(expected, actual, msg=msg)

        errors = []
        if missing:
            errors.append('Expected, but missing:\n    %s' % safe_repr(missing))
        if unexpected:
            errors.append('Unexpected, but present:\n    %s' % safe_repr(unexpected))
        if errors:
            standardMsg = '\n'.join(errors)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertMultiLineEqual(self, first, second, msg = None):
        self.assertIsInstance(first, basestring, 'First argument is not a string')
        self.assertIsInstance(second, basestring, 'Second argument is not a string')
        if first != second:
            firstlines = first.splitlines(True)
            secondlines = second.splitlines(True)
            if len(firstlines) == 1 and first.strip('\r\n') == first:
                firstlines = [first + '\n']
                secondlines = [second + '\n']
            standardMsg = '%s != %s' % (safe_repr(first, True), safe_repr(second, True))
            diff = '\n' + ''.join(difflib.ndiff(firstlines, secondlines))
            standardMsg = self._truncateMessage(standardMsg, diff)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLess(self, a, b, msg = None):
        if not a < b:
            standardMsg = '%s not less than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertLessEqual(self, a, b, msg = None):
        if not a <= b:
            standardMsg = '%s not less than or equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreater(self, a, b, msg = None):
        if not a > b:
            standardMsg = '%s not greater than %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertGreaterEqual(self, a, b, msg = None):
        if not a >= b:
            standardMsg = '%s not greater than or equal to %s' % (safe_repr(a), safe_repr(b))
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNone(self, obj, msg = None):
        if obj is not None:
            standardMsg = '%s is not None' % (safe_repr(obj),)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsNotNone(self, obj, msg = None):
        if obj is None:
            standardMsg = 'unexpectedly None'
            self.fail(self._formatMessage(msg, standardMsg))

    def assertIsInstance(self, obj, cls, msg = None):
        if not isinstance(obj, cls):
            standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotIsInstance(self, obj, cls, msg = None):
        if isinstance(obj, cls):
            standardMsg = '%s is an instance of %r' % (safe_repr(obj), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def assertRaisesRegexp(self, expected_exception, expected_regexp, callable_obj = None, *args, **kwargs):
        context = _AssertRaisesContext(expected_exception, self, expected_regexp)
        if callable_obj is None:
            return context
        with context:
            callable_obj(*args, **kwargs)

    def assertRegexpMatches(self, text, expected_regexp, msg = None):
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (msg, expected_regexp.pattern, text)
            raise self.failureException(msg)

    def assertNotRegexpMatches(self, text, unexpected_regexp, msg = None):
        if isinstance(unexpected_regexp, basestring):
            unexpected_regexp = re.compile(unexpected_regexp)
        match = unexpected_regexp.search(text)
        if match:
            msg = msg or 'Regexp matched'
            msg = '%s: %r matches %r in %r' % (msg,
             text[match.start():match.end()],
             unexpected_regexp.pattern,
             text)
            raise self.failureException(msg)


class FunctionTestCase(TestCase):

    def __init__(self, testFunc, setUp = None, tearDown = None, description = None):
        super(FunctionTestCase, self).__init__()
        self._setUpFunc = setUp
        self._tearDownFunc = tearDown
        self._testFunc = testFunc
        self._description = description

    def setUp(self):
        if self._setUpFunc is not None:
            self._setUpFunc()

    def tearDown(self):
        if self._tearDownFunc is not None:
            self._tearDownFunc()

    def runTest(self):
        self._testFunc()

    def id(self):
        return self._testFunc.__name__

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._setUpFunc == other._setUpFunc and self._tearDownFunc == other._tearDownFunc and self._testFunc == other._testFunc and self._description == other._description

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((type(self),
         self._setUpFunc,
         self._tearDownFunc,
         self._testFunc,
         self._description))

    def __str__(self):
        return '%s (%s)' % (strclass(self.__class__), self._testFunc.__name__)

    def __repr__(self):
        return '<%s tec=%s>' % (strclass(self.__class__), self._testFunc)

    def shortDescription(self):
        if self._description is not None:
            return self._description
        doc = self._testFunc.__doc__
        return doc and doc.split('\n')[0].strip() or None
