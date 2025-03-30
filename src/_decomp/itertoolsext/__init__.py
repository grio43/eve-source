#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itertoolsext\__init__.py
from brennivin.dochelpers import identity as _identity
from brennivin.itertoolsext import *
try:
    import uthread
except ImportError:
    uthread = None

_NOT_SUPPLIED = object()

def get_column(columnid, *rows):
    if not rows:
        return
    column_elements = zip(*rows)[columnid]
    return iter(column_elements)


def get_first_matching_index(iterable, predicate):
    for i, each in enumerate(iterable):
        if predicate(each):
            return i


def dump_dic(dic, indent = 0):
    buff = []
    ind = []
    for i in xrange(0, indent):
        ind.append('\t')

    ind = ''.join(ind)
    for k, v in dic.iteritems():
        if type(v) is dict:
            buff.append('%s%s = {\n' % (ind, k))
            buff.append(dump_dic(v, indent + 1))
            buff.append('%s}\n' % ind)
        else:
            buff.append('%s%s = %s %s\n' % (ind,
             k,
             v,
             type(v)))

    return ''.join(buff)


class IterTree(object):

    def __init__(self):
        self.nodes = {}

    def set(self, key_list, value):
        if isinstance(key_list, tuple):
            key_list = list(key_list)
        elif not isinstance(key_list, list):
            key_list = [key_list]
        key = key_list.pop(0)
        if key_list:
            if key not in self.nodes:
                self.nodes[key] = IterTree()
            self.nodes[key].set(key_list, value)
        else:
            self.nodes[key] = value

    def get(self, key_or_seq, default = _NOT_SUPPLIED):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            if default == _NOT_SUPPLIED:
                raise KeyError(key)
            else:
                return default
        else:
            if key_or_seq:
                return self.nodes[key].get(key_or_seq, default)
            return self.nodes[key]

    def __setitem__(self, key_list, value):
        self.set(key_list, value)

    def __getitem__(self, key_list):
        return self.get(key_list)

    def __len__(self):
        leaf_len = 0
        for n in self.nodes.itervalues():
            if isinstance(n, IterTree):
                leaf_len += len(n)
            else:
                leaf_len += 1

        return leaf_len

    def __iter__(self):
        return self.iterkeys()

    def __delitem__(self, key_or_seq):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            raise KeyError(key)
        elif key_or_seq:
            if isinstance(self.nodes[key], IterTree):
                self.nodes[key].__delitem__(key_or_seq)
                if len(self.nodes[key]) < 1:
                    del self.nodes[key]
            else:
                raise KeyError(key)
        else:
            del self.nodes[key]

    def popitem(self):
        for k in self.iterkeys():
            return (k, self.pop(k))

    def pop(self, key_or_seq, default = _NOT_SUPPLIED):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            if default == _NOT_SUPPLIED:
                raise KeyError(key)
            else:
                return default
        else:
            if key_or_seq:
                val = self.nodes[key].pop(key_or_seq, default)
                if len(self.nodes[key]) < 1:
                    del self.nodes[key]
                return val
            return self.nodes.pop(key)

    def __contains__(self, key_or_seq):
        if isinstance(key_or_seq, tuple):
            key_or_seq = list(key_or_seq)
        elif not isinstance(key_or_seq, list):
            key_or_seq = [key_or_seq]
        key = key_or_seq.pop(0)
        if key not in self.nodes:
            return False
        if key_or_seq:
            if isinstance(self.nodes[key], IterTree):
                return key_or_seq in self.nodes[key]
            else:
                return False
        else:
            return True

    def keys(self):
        key_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for c in n.iterkeys():
                    new_key = [k]
                    new_key.extend(c)
                    key_list.append(new_key)

            else:
                key_list.append([k])

        return [ tuple(k) for k in key_list ]

    def iterkeys(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for c in n.iterkeys():
                    next_key = [k]
                    next_key.extend(c)
                    yield tuple(next_key)

            else:
                yield (k,)

    def values(self):
        value_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for v in n.values():
                    value_list.append(v)

            else:
                value_list.append(n)

        return value_list

    def itervalues(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for v in n.itervalues():
                    yield v

            else:
                yield n

    def items(self):
        item_list = list()
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for nk, nv in n.items():
                    new_key = [k]
                    new_key.extend(nk)
                    item_list.append((new_key, nv))

            else:
                item_list.append(([k], n))

        return [ (tuple(ik), iv) for ik, iv in item_list ]

    def iteritems(self):
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                for nk, nv in n.iteritems():
                    next_key = [k]
                    next_key.extend(nk)
                    yield (tuple(next_key), nv)

            else:
                yield ((k,), n)

    def __repr__(self):
        buff = []
        for k, n in self.nodes.iteritems():
            buff.append('%s: %r' % (k, n))

        return '<IterTree [%s]>' % ', '.join(buff)

    def print_tree(self, _indent = 0):
        buff = []
        for k, n in self.nodes.iteritems():
            if isinstance(n, IterTree):
                buff.append('%s%s: {' % (' ' * (_indent * 4), k))
                buff.append(n.print_tree(_indent + 1))
                buff.append('%s}' % (' ' * (_indent * 4)))
            else:
                buff.append('%s%s: %r' % (' ' * (_indent * 4), k, n))

        return '\n'.join(buff)


def venn(left, right):
    left = set(left)
    right = set(right)
    return (list(left.difference(right)), list(left.intersection(right)), list(right.difference(left)))


def unique_sorted(seq, transform = _identity):
    item = next(iter(seq))
    last_marker = transform(item)
    yield item
    for item in seq:
        marker = transform(item)
        if marker == last_marker:
            continue
        last_marker = marker
        yield item


def merge_sorted(*seqs, **kwargs):
    if len(seqs) == 0:
        return iter([])
    elif len(seqs) == 1:
        return iter(seqs[0])
    key = kwargs.get('key', None)
    reverse = kwargs.get('reverse', False)
    if reverse:
        compare = lambda a, b: a > b
    else:
        compare = lambda a, b: a < b
    if key is None:
        return _merge_sorted_binary(seqs, compare)
    else:
        return _merge_sorted_binary_key(seqs, key, compare)


def _merge_sorted_binary(seqs, compare):
    mid = len(seqs) // 2
    L1 = seqs[:mid]
    if len(L1) == 1:
        seq1 = iter(L1[0])
    else:
        seq1 = _merge_sorted_binary(L1, compare)
    L2 = seqs[mid:]
    if len(L2) == 1:
        seq2 = iter(L2[0])
    else:
        seq2 = _merge_sorted_binary(L2, compare)
    try:
        val2 = next(seq2)
    except StopIteration:
        for val1 in seq1:
            yield val1

        return

    for val1 in seq1:
        if compare(val2, val1):
            yield val2
            for val2 in seq2:
                if compare(val2, val1):
                    yield val2
                else:
                    yield val1
                    break
            else:
                break

        else:
            yield val1
    else:
        yield val2
        for val2 in seq2:
            yield val2

        return

    yield val1
    for val1 in seq1:
        yield val1


def _merge_sorted_binary_key(seqs, key, compare):
    mid = len(seqs) // 2
    L1 = seqs[:mid]
    if len(L1) == 1:
        seq1 = iter(L1[0])
    else:
        seq1 = _merge_sorted_binary_key(L1, key, compare)
    L2 = seqs[mid:]
    if len(L2) == 1:
        seq2 = iter(L2[0])
    else:
        seq2 = _merge_sorted_binary_key(L2, key, compare)
    try:
        val2 = next(seq2)
    except StopIteration:
        for val1 in seq1:
            yield val1

        return

    key2 = key(val2)
    for val1 in seq1:
        key1 = key(val1)
        if compare(key2, key1):
            yield val2
            for val2 in seq2:
                key2 = key(val2)
                if compare(key2, key1):
                    yield val2
                else:
                    yield val1
                    break
            else:
                break

        else:
            yield val1
    else:
        yield val2
        for val2 in seq2:
            yield val2

        return

    yield val1
    for val1 in seq1:
        yield val1


def roundrobin(*iterables):
    num_active = len(iterables)
    nexts = cycle((iter(it).next for it in iterables))
    while num_active:
        try:
            for next in nexts:
                yield next()

        except StopIteration:
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))


_ITERABLE_TYPENAMES = ('List', 'Dict', 'StructureList')

def IsIterable(item):
    if isinstance(item, type):
        return False
    if uthread is not None and isinstance(item, uthread.Channel):
        return False
    if hasattr(item, '__typename__') and item.__typename__ in _ITERABLE_TYPENAMES:
        return True
    return hasattr(item, '__iter__')


def EnsureIterable(item):
    if item is None:
        return []
    elif not IsIterable(item):
        return [item]
    else:
        return item


is_iterable = IsIterable
ensure_iterable = EnsureIterable

def sort_tuples(seq, key = None, value = None, reverse = False):
    if key is None:

        def key(x):
            return x[0]

    if value is None:

        def value(x):
            return x[1]

    return [ value(x) for x in sorted(seq, key=key, reverse=reverse) ]
