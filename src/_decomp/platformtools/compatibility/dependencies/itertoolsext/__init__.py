#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\platformtools\compatibility\dependencies\itertoolsext\__init__.py
import six
if six.PY2:
    from itertoolsext import count, first_or_default, any, get_compound_attr, IsIterable, EnsureIterable
    from itertoolsext.Enum import SortedEnum, Enum
    from itertoolsext.StaticVariables import static_variables, StaticVariables
else:
    import functools
    from itertoolsext import count, first_or_default, any, get_compound_attr, IsIterable, EnsureIterable
    from itertoolsext.StaticVariables import static_variables, StaticVariables

    @StaticVariables(enumRegistry={})
    def Enum(cls):

        def GetIndex(self, item):
            for i, each in enumerate(self):
                if each == item:
                    return i

            return -1

        def ToString(self, item):
            for key, value in self.items():
                if value == item:
                    return str(key)

            return 'UNKNOWN'

        def GetEnumAsList(self):
            return [ (key, value) for key, value in self.items() ]

        def _FindKVByValue(self, value, tolerance = 0.005):
            if isinstance(value, float):
                for k, v in self.items():
                    if isinstance(v, float):
                        if abs(value - v) < tolerance:
                            return (k, v)

            else:
                for k, v in self.items():
                    if value == v:
                        return (k, v)

            return list(self.items())[0]

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

        def nested_list_compare(a, b):
            try:
                if isinstance(a, type(b)):
                    return (a > b) - (a < b)
                if a is None:
                    return -1
                if b is None:
                    return 1
                if isinstance(a, list):
                    return 1
                if isinstance(b, list):
                    return -1
                return (a > b) - (a < b)
            except TypeError:
                try:
                    if a > a or a < a:
                        return -1
                    return 1
                except TypeError:
                    return 1

        itemList = sorted(itemList, key=functools.cmp_to_key(nested_list_compare))
        cls.items = itemDict.items
        cls.keys = itemDict.keys
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
            for key, value in self.items():
                if value == item:
                    return str(key)

            return 'UNKNOWN'

        def GetEnumAsList(self):
            return [ (key, value) for key, value in self.items() ]

        def _FindKVByValue(self, value, tolerance = 0.005):
            if isinstance(value, float):
                for k, v in self.items():
                    if isinstance(v, float):
                        if abs(value - v) < tolerance:
                            return (k, v)

            else:
                for k, v in self.items():
                    if value == v:
                        return (k, v)

            return list(self.items())[0]

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
