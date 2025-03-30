#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\commonUtilities.py
import blue
from .paths import CompiledPath

class ValidationArgument(object):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if type(other) is type(self):
            return other.value == self.value
        return other == self.value

    def __ne__(self, other):
        if type(other) is type(self):
            return other.value != self.value
        return other != self.value

    @staticmethod
    def GetName():
        pass

    @staticmethod
    def GetTitle():
        raise NotImplementedError()

    @staticmethod
    def GetOptions():
        raise NotImplementedError()

    @staticmethod
    def CreateFromPath(path, root):
        raise NotImplementedError()

    @staticmethod
    def CreateFromObject(root):
        return None


class IsContent(ValidationArgument):
    CONTENT = 'content'
    BRANCH = 'branch'

    @staticmethod
    def GetName():
        return 'content'

    @staticmethod
    def GetTitle():
        return 'Is in content'

    @staticmethod
    def GetOptions():
        return [(IsContent.CONTENT, 'Content'), (IsContent.BRANCH, 'Branch')]

    @staticmethod
    def CreateFromPath(path, root):
        from devenv import content
        return IsContent(IsContent.CONTENT if content.IsContentPath(path.lower().replace('\\', '/')) else IsContent.BRANCH)


class SceneType(ValidationArgument):
    NOT_SCENE = 'na'
    GENERIC_SCENE = 'generic'
    HANGAR = 'hangar'

    @staticmethod
    def GetName():
        return 'scenetype'

    @staticmethod
    def GetTitle():
        return 'Scene type'

    @staticmethod
    def GetOptions():
        return [(SceneType.NOT_SCENE, 'Not A Scene'), (SceneType.GENERIC_SCENE, 'Generic Scene'), (SceneType.HANGAR, 'Hangar')]

    @staticmethod
    def CreateFromPath(path, root):
        if type(root).__name__ != 'EveSpaceScene':
            return SceneType(SceneType.NOT_SCENE)
        path = path.lower().replace('\\', '/')
        return SceneType(SceneType.HANGAR if '/model/hangar/' in path else SceneType.GENERIC_SCENE)

    @staticmethod
    def CreateFromObject(root):
        if type(root).__name__ == 'EveSpaceScene':
            return None
        return SceneType(SceneType.NOT_SCENE)


class BaseValidationRule(object):

    def __init__(self):
        self.name = None

    def CanApplyToTypeOf(self, value):
        return True

    def Applies(self, context):
        pass

    def GetArguments(self):
        return []

    def Apply(self, context):
        pass


def Validate(path, *args):

    class validationRule(BaseValidationRule):

        def __init__(self, func):
            super(validationRule, self).__init__()
            self._func = func
            self._path = CompiledPath(path)

        def CanApplyToTypeOf(self, value):
            if self._path.CanMatchTypeOf(value):
                return True
            if isinstance(self._func, BaseValidationRule):
                return self._func.CanApplyToTypeOf(value)
            return False

        def Applies(self, context):
            if isinstance(self._func, BaseValidationRule) and self._func.Applies(context):
                return True
            return self._path.Match(context.GetStack(), {})

        def GetArguments(self):
            result = []
            for each in args:
                if isinstance(each, type):
                    result.append(each)
                else:
                    result.append(type(each))

            if isinstance(self._func, BaseValidationRule):
                result.extend(self._func.GetArguments())
            return result

        def Apply(self, context):
            kwargs = {}
            if self._path.Match(context.GetStack(), kwargs):
                for each in args:
                    if not isinstance(each, type):
                        if each != context.GetArgument(type(each)):
                            return

                if kwargs:
                    self._func(context, **kwargs)
                else:
                    self._func(context, context.GetTop())
                return True
            if isinstance(self._func, BaseValidationRule):
                self._func.Apply(context)
            return False

        def __call__(self, *args, **kwargs):
            return self._func(*args, **kwargs)

    return validationRule


def IsIterator(obj):
    return isinstance(obj, (list, blue.List))


def AreEqual(first, second, attributesToCheck = None, attributesToIgnore = None):
    firstIsIterator = IsIterator(first)
    secondIsIterator = IsIterator(second)
    if firstIsIterator != secondIsIterator:
        return False
    elif firstIsIterator:
        return AreListsEqual(first, second, attributesToCheck, attributesToIgnore)
    else:
        return AreObjectsEqual(first, second, attributesToCheck, attributesToIgnore)


def AreListsEqual(first, second, attributesToCheck = None, attributesToIgnore = None):
    if len(first) != len(second):
        return False
    for f, s in zip(first, second):
        if not AreEqual(f, s, attributesToCheck, attributesToIgnore):
            return False

    return True


def AreObjectsEqual(first, second, attributesToCheck = None, attributesToIgnore = None):
    if type(first) != type(second):
        return False
    if attributesToCheck is None:
        attributesToCheck = [ attributeName for attributeName in dir(first) if not attributeName.startswith('_') and not callable(getattr(first, attributeName)) ]
    if attributesToIgnore is not None:
        for a in attributesToIgnore:
            attributesToCheck.remove(a)

    if len(attributesToCheck) == 0:
        return first == second
    if all([ getattr(first, attribute) == getattr(second, attribute) for attribute in attributesToCheck ]):
        return True
    return False


def DeleteAction(root, element, default):

    def inner():
        for route in blue.FindRoute(root, element):
            last = route[-1]
            if last[1] == 0:
                setattr(last[0], last[2], None)
            else:
                last[0].remove(element)
            return True

    return ('Delete %s' % (getattr(element, 'name', '') or type(element).__name__), inner, default)


def DeleteTopAction(context, default):
    return DeleteAction(context.GetStack()[0], context.GetTop(), default)


def GetDuplicateNames(genericList):
    duplicates = set()
    names = set()
    for each in genericList:
        name = getattr(each, 'name', '')
        if not name:
            continue
        if name in names:
            duplicates.add(name)
        else:
            names.add(name)

    return duplicates
