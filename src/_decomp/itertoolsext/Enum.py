#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itertoolsext\Enum.py
from .StaticVariables import *

@StaticVariables(enumRegistry={})
def Enum(cls):

    def GetIndex(self, item):
        for i, each in enumerate(self):
            if each == item:
                return i

        return -1

    def ToString(self, item):
        for key, value in self.iteritems():
            if value == item:
                return str(key)

        return 'UNKNOWN'

    def GetEnumAsList(self):
        return [ (key, value) for key, value in self.iteritems() ]

    def _FindKVByValue(self, value, tolerance = 0.005):
        if isinstance(value, float):
            for k, v in self.iteritems():
                if isinstance(v, float):
                    if abs(value - v) < tolerance:
                        return (k, v)

        else:
            for k, v in self.iteritems():
                if value == v:
                    return (k, v)

        return self.items()[0]

    def ValueToEnumValue(self, value, tolerance = 0.005):
        return _FindKVByValue(self, value, tolerance)[1]

    def ValueToEnumKey(self, value, tolerance = 0.005):
        return _FindKVByValue(self, value, tolerance)[0]

    if cls in Enum.enumRegistry:
        return Enum.enumRegistry[cls]
    items = [ x for x in dir(cls) if not x.startswith('__') ]
    if not items:
        instance = cls()
        Enum.enumRegistry[cls] = instance
        return instance
    itemList = []
    itemDict = {}
    for each in items:
        label = getattr(cls, each)
        itemList.append(label)
        itemDict[each] = label

    itemList = sorted(itemList)
    cls.iteritems = itemDict.iteritems
    cls.iterkeys = itemDict.iterkeys
    cls.itervalues = itemDict.itervalues
    cls.items = itemDict.items
    cls.keys = itemDict.keys
    cls.values = itemDict.values
    cls.__iter__ = itemList.__iter__
    cls.__getitem__ = itemList.__getitem__
    cls.__len__ = itemList.__len__
    cls.GetIndex = GetIndex
    cls.ToString = ToString
    cls.GetEnumAsList = GetEnumAsList
    cls.ValueToEnumValue = ValueToEnumValue
    cls.ValueToEnumKey = ValueToEnumKey
    instance = cls()
    Enum.enumRegistry[cls] = instance
    return instance


@StaticVariables(enumRegistry={})
def SortedEnum(cls):

    def GetIndex(self, item):
        for i, each in enumerate(self):
            if each == item:
                return i

        return -1

    def ToString(self, item):
        for key, value in self.iteritems():
            if value == item:
                return str(key)

        return 'UNKNOWN'

    def GetEnumAsList(self):
        return [ (key, value) for key, value in self.iteritems() ]

    def _FindKVByValue(self, value, tolerance = 0.005):
        if isinstance(value, float):
            for k, v in self.iteritems():
                if isinstance(v, float):
                    if abs(value - v) < tolerance:
                        return (k, v)

        else:
            for k, v in self.iteritems():
                if value == v:
                    return (k, v)

        return self.items()[0]

    def ValueToEnumValue(self, value, tolerance = 0.005):
        return _FindKVByValue(self, value, tolerance)[1]

    def ValueToEnumKey(self, value, tolerance = 0.005):
        return _FindKVByValue(self, value, tolerance)[0]

    if cls in Enum.enumRegistry:
        return Enum.enumRegistry[cls]
    items = [ x for x in dir(cls) if not x.startswith('__') ]
    if not items:
        instance = cls()
        Enum.enumRegistry[cls] = instance
        return instance
    itemList = []
    itemDict = []
    items = sorted(items, key=lambda a: getattr(cls, a)[1])
    for each in items:
        item = getattr(cls, each)
        label = item[0]
        setattr(cls, each, label)
        itemList.append(label)
        itemDict.append((each, label))

    cls.iteritems = itemDict.__iter__
    cls.iterkeys = itemList
    cls.items = itemDict.__iter__
    cls.keys = itemList
    cls.__iter__ = itemList.__iter__
    cls.__getitem__ = itemList.__getitem__
    cls.__len__ = itemList.__len__
    cls.GetIndex = GetIndex
    cls.ToString = ToString
    cls.GetEnumAsList = GetEnumAsList
    cls.ValueToEnumValue = ValueToEnumValue
    cls.ValueToEnumKey = ValueToEnumKey
    instance = cls()
    Enum.enumRegistry[cls] = instance
    return instance


enum = Enum
sorted_enum = SortedEnum
