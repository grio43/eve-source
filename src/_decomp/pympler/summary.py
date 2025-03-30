#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pympler\summary.py
import re
import sys
import types
from pympler.util import stringutils
try:
    from sys import getsizeof as _getsizeof
except ImportError:
    from pympler.asizeof import flatsize
    _getsizeof = flatsize

representations = {}

def _init_representations():
    global representations
    if sys.hexversion < 33816576:
        classobj = [lambda c: 'classobj(%s)' % repr(c)]
        representations[types.ClassType] = classobj
        instance = [lambda f: 'instance(%s)' % repr(f.__class__)]
        representations[types.InstanceType] = instance
        instancemethod = [lambda i: 'instancemethod (%s)' % repr(i.im_func), lambda i: 'instancemethod (%s, %s)' % (repr(i.im_class), repr(i.im_func))]
        representations[types.MethodType] = instancemethod
    frame = [lambda f: 'frame (codename: %s)' % f.f_code.co_name, lambda f: 'frame (codename: %s, codeline: %s)' % (f.f_code.co_name, f.f_code.co_firstlineno), lambda f: 'frame (codename: %s, filename: %s, codeline: %s)' % (f.f_code.co_name, f.f_code.co_filename, f.f_code.co_firstlineno)]
    representations[types.FrameType] = frame
    _dict = [lambda d: str(type(d)), lambda d: 'dict, len=%s' % len(d)]
    representations[dict] = _dict
    function = [lambda f: 'function (%s)' % f.__name__, lambda f: 'function (%s.%s)' % (f.__module, f.__name__)]
    representations[types.FunctionType] = function
    _list = [lambda l: str(type(l)), lambda l: 'list, len=%s' % len(l)]
    representations[list] = _list
    module = [lambda m: 'module(%s)' % m.__name__]
    representations[types.ModuleType] = module
    _set = [lambda s: str(type(s)), lambda s: 'set, len=%s' % len(s)]
    representations[set] = _set


_init_representations()

def summarize(objects):
    count = {}
    total_size = {}
    for o in objects:
        otype = _repr(o)
        if otype in count:
            count[otype] += 1
            total_size[otype] += _getsizeof(o)
        else:
            count[otype] = 1
            total_size[otype] = _getsizeof(o)

    rows = []
    for otype in count:
        rows.append([otype, count[otype], total_size[otype]])

    return rows


def get_diff(left, right):
    res = []
    for row_r in right:
        found = False
        for row_l in left:
            if row_r[0] == row_l[0]:
                res.append([row_r[0], row_r[1] - row_l[1], row_r[2] - row_l[2]])
                found = True

        if not found:
            res.append(row_r)

    for row_l in left:
        found = False
        for row_r in right:
            if row_l[0] == row_r[0]:
                found = True

        if not found:
            res.append([row_l[0], -row_l[1], -row_l[2]])

    return res


def format_(rows, limit = 15, sort = 'size', order = 'descending'):
    localrows = []
    for row in rows:
        localrows.append(list(row))

    sortby = ['type', '#', 'size']
    if sort not in sortby:
        raise ValueError('invalid sort, should be one of' + str(sortby))
    orders = ['ascending', 'descending']
    if order not in orders:
        raise ValueError('invalid order, should be one of' + str(orders))
    if sortby.index(sort) == 0:
        if order == 'ascending':
            localrows.sort(key=lambda x: _repr(x[0]))
        elif order == 'descending':
            localrows.sort(key=lambda x: _repr(x[0]), reverse=True)
    elif order == 'ascending':
        localrows.sort(key=lambda x: x[sortby.index(sort)])
    elif order == 'descending':
        localrows.sort(key=lambda x: x[sortby.index(sort)], reverse=True)
    localrows = localrows[0:limit]
    for row in localrows:
        row[2] = stringutils.pp(row[2])

    localrows.insert(0, ['types', '# objects', 'total size'])
    return _format_table(localrows)


def _format_table(rows, header = True):
    border = '='
    vdelim = ' | '
    padding = 1
    justify = 'right'
    justify = {'left': str.ljust,
     'center': str.center,
     'right': str.rjust}[justify.lower()]
    cols = zip(*rows)
    colWidths = [ max([ len(str(item)) + 2 * padding for item in col ]) for col in cols ]
    borderline = vdelim.join([ w * border for w in colWidths ])
    for row in rows:
        yield vdelim.join([ justify(str(item), width) for item, width in zip(row, colWidths) ])
        if header:
            yield borderline
            header = False


def print_(rows, limit = 15, sort = 'size', order = 'descending'):
    for line in format_(rows, limit=limit, sort=sort, order=order):
        print line


type_prefix = re.compile("^<type '")
address = re.compile(' at 0x[0-9a-f]+')
type_suffix = re.compile("'>$")

def _repr(o, verbosity = 1):
    res = ''
    t = type(o)
    if verbosity == 0 or t not in representations:
        res = str(t)
    else:
        verbosity -= 1
        if len(representations[t]) < verbosity:
            verbosity = len(representations[t]) - 1
        res = representations[t][verbosity](o)
    res = address.sub('', res)
    res = type_prefix.sub('', res)
    res = type_suffix.sub('', res)
    return res


def _traverse(summary, function, *args):
    function(summary, *args)
    for row in summary:
        function(row, *args)
        for item in row:
            function(item, *args)


def _subtract(summary, o):
    found = False
    row = [_repr(o), 1, _getsizeof(o)]
    for r in summary:
        if r[0] == row[0]:
            r[1], r[2] = r[1] - row[1], r[2] - row[2]
            found = True

    if not found:
        summary.append([row[0], -row[1], -row[2]])
    return summary


def _sweep(summary):
    return [ row for row in summary if row[2] != 0 or row[1] != 0 ]
