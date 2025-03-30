#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\rowset.py
import _weakref
import __builtin__
import types
import string
import weakref
import sys
import uthread
import copy
import blue
from carbon.common.script.sys.row import Row as utilRow
import log

def Select(selection, headers, iterator, options):
    if len(selection) == 1:
        i = headers.index(selection[0])
        if options.get('line', False):
            return [ (line, line[i]) for line in iterator ]
        else:
            return [ line[i] for line in iterator ]
    else:
        indices = []
        for header in selection:
            indices.append(headers.index(header))

        if options.get('line', False):
            return [ (line, [ line[i] for i in indices ]) for line in iterator ]
        return [ [ line[i] for i in indices ] for line in iterator ]


class Rowset:
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = utilRow

    def __init__(self, hd = None, li = None, RowClass = utilRow):
        if hd is None:
            hd = []
        if li is None:
            li = []
        self.header = hd
        self.lines = li
        self.RowClass = RowClass

    def Clone(self):
        return Rowset(copy.copy(self.header), copy.copy(self.lines), self.RowClass)

    def IsImmutable(self):
        return self in self.__immutable__

    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = [{}, {}]

    def __str__(self):
        try:
            stuff = []
            for eachRow in self:
                stuff.append(strx(eachRow))

            return '<Rowset: header=%s, data=["' % strx(self.header) + string.join(stuff, '","') + '"]>'
        except:
            sys.exc_clear()
            return 'Rowset, hd=' + strx(self.header)

    def __len__(self):
        return len(self.lines)

    def RenameField(self, oldName, newName):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        for i in range(len(self.header)):
            if self.header[i] == oldName:
                self.header[i] = newName
                return

        log.LogTraceback()
        raise RuntimeError('No Such Field')

    def AddField(self, fieldName, value):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(self.lines) and type(self.lines[0]) == type(()):
            raise RuntimeError('CannotAddFieldsToATupleRowset', self)
        self.header.append(fieldName)
        for l in self.lines:
            l.append(value)

    def RemoveField(self, fieldName):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(self.lines) and type(self.lines[0]) == type(()):
            raise RuntimeError('CannotRemoveFieldsFromATupleRowset', self)
        idx = self.header.index(fieldName)
        del self.header[idx]
        for l in self.lines:
            del l[idx]

    def find(self, column, value):
        h = self.header.index(column)
        for i in xrange(len(self.lines)):
            if self.lines[i][h] == value:
                return i

        return -1

    def Select(self, *selection, **options):
        return Select(selection, self.header, self.lines, options)

    def __getitem__(self, index):
        return self.RowClass(self.header, self.lines[index])

    def __setitem__(self, i, v):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if type(v) == types.InstanceType:
            self[i] = v.line
            return
        if len(v):
            if len(v) > len(self.header):
                raise RuntimeError('Too many columns, got %s, fields are %s' % (len(v), self.header))
            self.lines[i] = list(v) + [None] * (len(self.header) - len(v))
        else:
            self.lines[i] = [None] * len(self.header)

    def __getslice__(self, i, j):
        return Rowset(self.header, self.lines[i:j], self.RowClass)

    def __delitem__(self, index):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        del self.lines[index]

    def sort(self, f = None):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if f is not None:
            self.lines.sort(f)
        else:
            self.lines.sort()

    def extend(self, other):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        self.lines.extend(other.lines)

    def remove(self, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        try:
            self.lines.remove(row.line)
        except ValueError:
            sys.exc_clear()
        except AttributeError:
            sys.exc_clear()
            self.lines.remove(row)

    def pop(self, idx):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        return self.RowClass(self.header, self.lines.pop(idx))

    def InsertNew(self, *args):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if len(args):
            if len(args) > len(self.header):
                raise RuntimeError('Too many arguments, got %s, fields are %s' % (len(args), self.header))
            self.lines.append(list(args) + [None] * (len(self.header) - len(args)))
        else:
            self.lines.append([None] * len(self.header))
        return self[-1]

    def Sort(self, colname, asc = 1):
        ret = self[:]
        if asc:
            ret.lines.sort(lambda a, b, colid = self.header.index(colname): -(a[colid] < b[colid]))
        else:
            ret.lines.sort(lambda b, a, colid = self.header.index(colname): -(a[colid] < b[colid]))
        return ret

    def Index(self, colname):
        if self in self.__immutable__:
            uthread.Lock(self, '__immutable__', colname)
            try:
                if colname not in self.__immutable__[self][0]:
                    ret = IndexRowset(self.header, self.lines, colname)
                    self.__immutable__[self][0][colname] = ret
                    ret.MakeImmutable()
                return self.__immutable__[self][0][colname]
            finally:
                uthread.UnLock(self, '__immutable__', colname)

        else:
            return IndexRowset(self.header, self.lines, colname)

    def Filter(self, colname, colname2 = None):
        if self in self.__immutable__:
            k = (colname, colname2)
            uthread.Lock(self, '__immutable__', k)
            try:
                if k not in self.__immutable__[self][1]:
                    ret = FilterRowset(self.header, self.lines, colname, idName2=colname2)
                    ret.MakeImmutable()
                    self.__immutable__[self][1][k] = ret
                return self.__immutable__[self][1][k]
            finally:
                uthread.UnLock(self, '__immutable__', k)

        else:
            return FilterRowset(self.header, self.lines, colname, idName2=colname2)

    def append(self, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable Rowsets may not be modified')
        if type(row) == type([]):
            if len(row) != len(self.header):
                raise RuntimeError('Invalid row length for appending', self, row)
            self.lines.append(row)
        else:
            if len(self.header) != len(row.header):
                raise RuntimeError('Invalid header for appending', self, row)
            self.lines.append(row.line)


class IndexOrFilterRowsetIterator:

    def __init__(self, rowset, iterator):
        self.rowset = _weakref.proxy(rowset)
        self.iterator = iterator

    def next(self):
        return self.rowset.RowClass(self.rowset.header, self.iterator.next())


class IndexRowset:
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = utilRow
    stacktraceCnt = 0

    def __init__(self, header = None, li = (), idName = None, RowClass = utilRow, dict = None):
        if dict is not None:
            self.items = dict
        elif header is not None and li is not None:
            idfield = header.index(idName)
            self.items = __builtin__.dict([ (i[idfield], i) for i in li ])
        else:
            self.items = {}
        self.header = header
        self.RowClass = RowClass
        self.idName = idName

    def GetKeyColumn(self):
        return self.idName

    def GetLine(self, key):
        return self.items[key]

    def Clone(self):
        return IndexRowset(copy.copy(self.header), None, self.idName, self.RowClass, copy.copy(self.items))

    def IsImmutable(self):
        return self in self.__immutable__

    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = 1

    def Select(self, *selection, **options):
        return Select(selection, self.header, self.items.itervalues(), options)

    def __iter__(self):
        return iter(self.items)

    def __contains__(self, key):
        return key in self.items

    def __getitem__(self, i):
        return self.RowClass(self.header, self.items[i])

    def __len__(self):
        return len(self.items)

    def values(self):
        return Rowset(self.header, self.items.values(), self.RowClass)

    def itervalues(self):
        return self.values()

    def keys(self):
        return self.items.keys()

    def iterkeys(self):
        return self.items.iterkeys()

    def iteritems(self):
        return self.items.iteritems()

    def has_key(self, key):
        return self.items.has_key(key)

    def __setitem__(self, ind, row):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        if type(row) == type([]):
            self.items[ind] = row
        else:
            if hasattr(row, '__columns__'):
                rowHeader = row.__columns__
                rowLine = list(row)
            else:
                rowHeader = row.header
                rowLine = row.line
            if len(self.header) != len(rowHeader):
                line = [None] * len(self.header)
                for i in range(len(self.header)):
                    cname = self.header[i]
                    try:
                        idx = rowHeader.index(cname)
                    except ValueError:
                        raise RuntimeError('Mismatched row headers - game is broken', self.header, rowHeader)

                    line[i] = rowLine[idx]

                if self.stacktraceCnt < 2:
                    log.LogTraceback('rowset')
                    self.stacktraceCnt += 1
                self.items[ind] = line
            else:
                self.items[ind] = rowLine

    def __delitem__(self, ind):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        del self.items[ind]

    def Sort(self, colname):
        ret = self.values()
        return ret.Sort(colname)

    def get(self, ind, defValue):
        try:
            return self[ind]
        except:
            sys.exc_clear()
            return defValue

    def UpdateLI(self, lines, indexName, overWrite = 0):
        if self in self.__immutable__:
            raise RuntimeError('Immutable IndexRowsets may not be modified')
        ind = self.header.index(indexName)
        for i in lines:
            if not (not overWrite and self.items.has_key(i[ind])):
                self.items[i[ind]] = i

    def Map(self, indexes):
        ret = Rowset(self.header, [])
        for i in indexes:
            if self.has_key(i):
                ret.append(self[i])

        return ret

    def __str__(self):
        stuff = {}
        for key in self.iterkeys():
            eachRow = self[key]
            stuff[key] = eachRow

        return '<IndexRowset: header=%s, data=' % strx(self.header) + strx(stuff).replace('"', '') + '>'


class FilterRowset:
    __guid__ = 'util.FilterRowset'
    __passbyvalue__ = 1
    __immutable__ = weakref.WeakKeyDictionary()
    RowClass = utilRow

    def __init__(self, header = None, li = None, idName = None, RowClass = utilRow, idName2 = None, dict = None):
        items = {}
        self.RowClass = RowClass
        if dict is not None:
            items = dict
        elif header is not None:
            if not idName2:
                idfield = header.index(idName)
                for i in li:
                    id = i[idfield]
                    if id in items:
                        items[id].append(i)
                    else:
                        items[id] = [i]

            else:
                idfield = header.index(idName)
                idfield2 = header.index(idName2)
                for i in li:
                    id = i[idfield]
                    if id in items:
                        items[id][i[idfield2]] = i
                    else:
                        items[id] = {i[idfield2]: i}

        self.items = items
        self.header = header
        self.idName = idName
        self.idName2 = idName2

    def Clone(self):
        return FilterRowset(copy.copy(self.header), None, self.idName, self.RowClass, self.idName2, dict=copy.deepcopy(self.items))

    def IsImmutable(self):
        return self in self.__immutable__

    def MakeImmutable(self):
        if self not in self.__immutable__:
            self.__immutable__[self] = 1

    def __iter__(self):
        return IndexOrFilterRowsetIterator(self, self.items.iterkeys())

    def __contains__(self, key):
        return key in self.items

    def has_key(self, key):
        return key in self.items

    def get(self, key, val):
        try:
            return self[key]
        except:
            sys.exc_clear()
            return val

    def keys(self):
        return self.items.keys()

    def iterkeys(self):
        return self.items.iterkeys()

    def __getitem__(self, i):
        if self.idName2:
            return IndexRowset(self.header, None, self.idName2, self.RowClass, self.items.get(i, {}))
        return Rowset(self.header, self.items.get(i, []), self.RowClass)

    def __len__(self):
        return len(self.items)

    def Sort(self, colname):
        ret = Rowset(self.header, self.items.values(), self.RowClass)
        return ret.Sort(colname)

    def GetIndexKeys(self):
        if self.idName2 is not None:
            return (self.idName, self.idName2)
        return (self.idName,)

    def GetLines(self, idValue, idValue2 = None):
        if self.idName2 is not None:
            return self.items[idValue][idValue2]
        return self.items[idValue]


def RowsInit(rows, columns):
    header = None
    if type(rows) is types.TupleType:
        header = rows[0]
        rows = rows[1]
    if rows:
        first = rows[0]
        if type(first) != blue.DBRow:
            raise AttributeError('Not DBRow. Initialization requires a non-empty list of DBRows')
        header = first.__header__
    elif header:
        if type(header) != blue.DBRowDescriptor:
            raise AttributeError('expected (DBRowDesciptor, [])')
    if header:
        columns = header.Keys()
    return (rows, columns, header)


class RowDict(dict):
    __guid__ = 'dbutil.RowDict'
    __passbyvalue__ = 1
    slots = ['columns', 'header', 'key']

    def __init__(self, rowList, key, columns = None):
        dict.__init__(self)
        rows, self.columns, self.header = RowsInit(rowList, columns)
        if key not in self.columns:
            raise AttributeError('Indexing key not found in row')
        self.key = key
        for row in rows:
            self[row[key]] = row

    def ReIndex(self, key):
        if key not in self.columns:
            raise AttributeError('Indexing key not found in columns')
        vals = self.values()
        self.clear()
        self.key = key
        for row in vals:
            self[row[self.key]] = row

    def Add(self, row):
        if type(row) != blue.DBRow:
            raise AttributeError('Not DBRow')
        if row.__columns__ != self.columns:
            raise ValueError('Incompatible rows')
        if self.header is None:
            self.header = row.__header__
        self[row[self.key]] = row


class RowList(list):
    __guid__ = 'dbutil.RowList'
    __passbyvalue__ = 1
    slots = ['header', 'columns']

    def __init__(self, rowList, columns = None):
        list.__init__(self)
        rows, self.columns, self.header = RowsInit(rowList, columns)
        self[:] = rows

    def append(self, row):
        if type(row) != blue.DBRow:
            raise ValueError('Not DBRow')
        if row.__columns__ != self.columns:
            raise ValueError('Incompatible headers')
        if self.header is None:
            self.header = row.__header__
        list.append(self, row)


class IndexedRows(dict):
    __guid__ = 'util.IndexedRows'
    __passbyvalue__ = 1

    def __init__(self, rows = [], keys = None):
        self.InsertMany(keys, rows)

    def InsertMany(self, keys, rows):
        for r in rows:
            self.Insert(keys, r)

    def Insert(self, keys, e):
        key, rkeys = keys[0], keys[1:]
        if rkeys:
            if e[key] not in self:
                self[e[key]] = IndexedRows()
            self[e[key]].Insert(rkeys, e)
        else:
            self[e[key]] = e


class IndexedRowLists(dict):
    __guid__ = 'util.IndexedRowLists'
    __passbyvalue__ = 1

    def __init__(self, rows = [], keys = None):
        self.header = []
        self.InsertMany(keys, rows)

    def InsertMany(self, keys, rows):
        for r in rows:
            self.Insert(keys, r)

    def Insert(self, keys, e):
        key, rkeys = keys[0], keys[1:]
        self.header = [key]
        if rkeys:
            if e[key] not in self:
                self[e[key]] = IndexedRowLists()
            self[e[key]].Insert(rkeys, e)
        else:
            if e[key] not in self:
                self[e[key]] = []
            self[e[key]].append(e)

    def GetIndexKeys(self):
        l = self.header[:]
        for v in self.itervalues():
            if isinstance(v, self.__class__):
                l.extend(v.GetIndexKeys())
            break

        return l

    def GetLines(self, firstKey, *nextKeys):
        ret = self[firstKey]
        if len(nextKeys):
            return ret.GetLines(*nextKeys)
        return ret
