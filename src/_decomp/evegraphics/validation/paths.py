#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\paths.py
import re

class PathComponentType(object):
    ANY_CHILD = 1
    ANY_DESCENDANT = 2
    TYPE = 3
    LIST = 4
    TYPE_EXACT = 5
    TYPE_EXACT_WITH = 6


def _GetPythonInterfaces(valueType):
    yield valueType.__name__
    for each in valueType.__bases__:
        for name in _GetPythonInterfaces(each):
            yield name


def _GetBlueInterfaces(value):
    try:
        info = value.TypeInfo()
    except AttributeError:
        return set()

    return set(info[1].keys())


def _GetInterfaces(value):
    interfaces = _GetBlueInterfaces(value)
    interfaces.update(set(_GetPythonInterfaces(type(value))))
    return interfaces


_interfaces = {}

def _IsInstance(value, typeName):
    interfaces = _interfaces.get(type(value), None)
    if interfaces is None:
        interfaces = _GetInterfaces(value)
        _interfaces[type(value)] = interfaces
    return typeName in interfaces


class CompiledPath(object):

    def __init__(self, path):
        components = path.split('/')
        self._components = []
        self._hasAnyDescendantComponents = False
        if components[0] == '':
            components = components[1:]
        else:
            self._components.append((PathComponentType.ANY_DESCENDANT,
             '',
             '',
             '',
             ''))
            self._hasAnyDescendantComponents = True
        self._capturingComponentsCount = 0
        for each in components:
            if each == '':
                raise ValueError('invalid validation path "%s"' % path)
            elif each == '...':
                self._components.append((PathComponentType.ANY_DESCENDANT,
                 '',
                 '',
                 '',
                 ''))
                self._hasAnyDescendantComponents = True
            else:
                self._capturingComponentsCount += 1
                match = re.match('\\*(\\((\\w+)+\\))?', each)
                if match:
                    self._components.append((PathComponentType.ANY_CHILD,
                     '',
                     match.group(2),
                     '',
                     ''))
                else:
                    match = re.match('List\\[(\\w+)\\](\\((\\w+)+\\))?', each)
                    if match:
                        self._components.append((PathComponentType.LIST,
                         match.group(1),
                         match.group(3),
                         '',
                         ''))
                    else:
                        match = re.match('(=?)(\\w+)(\\((\\w+))(.+with=)(\\w+)(\\((\\w+)+\\))?', each)
                        if match:
                            self._components.append((PathComponentType.TYPE_EXACT_WITH,
                             match.group(2),
                             match.group(4),
                             match.group(6),
                             match.group(8)))
                        else:
                            match = re.match('(=?)(\\w+)(\\((\\w+)+\\))?', each)
                            if not match:
                                raise ValueError('invalid validation path "%s"' % path)
                            if match.group(1):
                                self._components.append((PathComponentType.TYPE_EXACT,
                                 match.group(2),
                                 match.group(4),
                                 '',
                                 ''))
                            else:
                                self._components.append((PathComponentType.TYPE,
                                 match.group(2),
                                 match.group(4),
                                 '',
                                 ''))

        if not self._components:
            raise ValueError('invalid validation path "%s"' % path)
        self._lastComponentIndex = len(self._components) - 1
        self._quickMatch = None
        if len(self._components) == 2 and self._components[0][0] == PathComponentType.ANY_DESCENDANT and self._components[1][0] == PathComponentType.TYPE:
            self._quickMatch = self._MatchSingleType
        elif len(self._components) == 2 and self._components[0][0] == PathComponentType.ANY_DESCENDANT and self._components[1][0] == PathComponentType.TYPE_EXACT:
            self._quickMatch = self._MatchSingleTypeExact
        self._quickTypeMatch = lambda _: True
        if len(self._components) > 0:
            if self._components[-1][0] == PathComponentType.TYPE:
                self._quickTypeMatch = self._CanMatchSingleType
            elif self._components[-1][0] in (PathComponentType.TYPE_EXACT, PathComponentType.TYPE_EXACT_WITH):
                self._quickTypeMatch = self._CanMatchSingleTypeExact
            elif self._components[-1][0] == PathComponentType.LIST:
                self._quickTypeMatch = self._CanMatchList

    def _MatchSingleType(self, stack, variables):
        if _IsInstance(stack[-1], self._components[1][1]):
            if self._components[1][2]:
                variables[self._components[1][2]] = stack[-1]
            return True
        return False

    def _MatchSingleTypeExact(self, stack, variables):
        if type(stack[-1]).__name__ == self._components[1][1]:
            if self._components[1][2]:
                variables[self._components[1][2]] = stack[-1]
            return True
        return False

    def _CanMatchSingleType(self, value):
        return _IsInstance(value, self._components[-1][1])

    def _CanMatchSingleTypeExact(self, value):
        return type(value).__name__ == self._components[-1][1]

    def _CanMatchList(self, value):
        blueType = getattr(value, '__bluetype__', '')
        return blueType == 'blue.List' or not blueType and isinstance(value, list)

    def CanMatchTypeOf(self, value):
        return self._quickTypeMatch(value)

    def Match(self, stack, variables):
        if self._quickMatch:
            return self._quickMatch(stack, variables)
        stackLength = len(stack)
        if self._hasAnyDescendantComponents:
            if stackLength < self._capturingComponentsCount:
                return False
        elif stackLength != self._capturingComponentsCount:
            return False
        return self._Match(stack, stackLength - 1, self._components, self._lastComponentIndex, variables)

    def _Match(self, stack, stackIndex, components, componentIndex, variables):
        if componentIndex < 0:
            if stackIndex < 0:
                return True
            else:
                return False
        elif stackIndex < 0:
            if componentIndex == 0 and components[componentIndex][0] == PathComponentType.ANY_DESCENDANT:
                return True
            return False
        kind, typeName, varName, childType, childVar = components[componentIndex]
        item = stack[stackIndex]
        if kind == PathComponentType.TYPE:
            if _IsInstance(item, typeName):
                if varName:
                    variables[varName] = item
                return self._Match(stack, stackIndex - 1, components, componentIndex - 1, variables)
            return False
        elif kind == PathComponentType.ANY_CHILD:
            if varName:
                variables[varName] = item
            return self._Match(stack, stackIndex - 1, components, componentIndex - 1, variables)
        elif kind == PathComponentType.ANY_DESCENDANT:
            if componentIndex == 0:
                return True
            for i in range(stackIndex, -1, -1):
                result = self._Match(stack, i, components, componentIndex - 1, variables)
                if result:
                    return result

            return False
        elif kind == PathComponentType.LIST:
            blueType = getattr(item, '__bluetype__', '')
            if blueType == 'blue.List' or not blueType and isinstance(item, list):
                if blueType:
                    if item.GetInfo()[1][0] != typeName:
                        return False
                else:
                    for each in item:
                        if type(each).__name__ != typeName:
                            return False

                if varName:
                    variables[varName] = item
                return self._Match(stack, stackIndex - 1, components, componentIndex - 1, variables)
            return False
        elif kind == PathComponentType.TYPE_EXACT:
            if type(item).__name__ == typeName:
                if varName:
                    variables[varName] = item
                return self._Match(stack, stackIndex - 1, components, componentIndex - 1, variables)
            return False
        elif kind == PathComponentType.TYPE_EXACT_WITH:
            if type(item).__name__ == typeName:
                try:
                    import blue
                    children = blue.FindInterface(item, childType)
                    if varName and children and childVar:
                        variables[varName] = item
                        variables[childVar] = children
                        return self._Match(stack, stackIndex - 1, components, componentIndex - 1, variables)
                    return False
                except:
                    pass

            return False
        else:
            return False
