#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\__init__.py
import os
import time
import sys
from evegraphics.validation.commonUtilities import BaseValidationRule
from evegraphics.validation.errors import SingleObjectValidationError, ValidationError, MultipleValidationErrors
import blue
import trinity

def GetObjectAttribute(obj, attribute):
    if attribute is not None:
        if hasattr(obj, attribute):
            return getattr(obj, attribute)
        else:
            print "object '%s' has no attribute '%s'" % (obj, attribute)
            return
    return obj


def _FormatPath(stack):
    return '/'.join(((getattr(x, 'name') if getattr(x, 'name', '') else type(x).__name__) for x in stack))


_jessicaSkipValidationObjects = {}

def ValidationAttributeFilter(obj, attr):
    try:
        return _jessicaSkipValidationObjects[type(obj), attr]
    except KeyError:
        try:
            use = ':jessica-skip-validation:' not in obj.TypeInfo()[2][attr]['description']
        except Exception:
            use = True

        _jessicaSkipValidationObjects[type(obj), attr] = use
        return use


class ObjectLink(object):

    def GetSourceObject(self):
        return None

    def GetBinding(self):
        return None

    def GetBoundObject(self):
        raise NotImplementedError()

    def GetBoundAttribute(self):
        raise NotImplementedError()

    def SetBoundAttribute(self, attr):
        raise NotImplementedError()

    def Patch(self, old, new):
        raise NotImplementedError()

    def IsDestination(self):
        raise NotImplementedError()

    def IsSource(self):
        raise NotImplementedError()


class ControllerActionLink(ObjectLink):

    def __init__(self, action, parentController):
        self._action = action
        self._parentController = parentController

    def GetBoundObject(self):
        boundObject = self._action.GetDestination()
        if not boundObject and self._action.delayBinding:
            boundObject = trinity.ResolveObjectPath(self._action.path, {'Owner': self._parentController.GetOwner()})
        return boundObject

    def GetBoundAttribute(self):
        return self._action.attribute

    def SetBoundAttribute(self, attr):
        self._action.attribute = attr

    def IsDestination(self):
        return True

    def IsSource(self):
        return False

    def Patch(self, old, new):
        if self.GetBoundObject() == old:
            if self._action.path:
                raise NotImplementedError()
            else:
                self._action.destination = new
            return True
        return False


class SourceBindingLink(ObjectLink):

    def __init__(self, binding):
        self._binding = binding

    def GetBinding(self):
        return self._binding

    def GetBoundObject(self):
        return self._binding.sourceObject

    def GetBoundAttribute(self):
        return self._binding.sourceAttribute

    def SetBoundAttribute(self, attr):
        self._binding.sourceAttribute = attr

    def Patch(self, old, new):
        if self.GetBoundObject() == old:
            self._binding.sourceObject = new
            return True
        return False

    def IsDestination(self):
        return False

    def IsSource(self):
        return True


class SourceDynamicBindingLink(ObjectLink):

    def __init__(self, binding):
        self._binding = binding

    def GetBinding(self):
        return self._binding

    def GetBoundObject(self):
        return self._binding.source

    def GetBoundAttribute(self):
        return self._binding.sourceObjectAttribute

    def SetBoundAttribute(self, attr):
        self._binding.sourceObjectAttribute = attr

    def Patch(self, old, new):
        if self.GetBoundObject() == old:
            self._binding.source = new
            return True
        return False

    def IsDestination(self):
        return False

    def IsSource(self):
        return True


class DestinationBindingLink(ObjectLink):

    def __init__(self, binding):
        self._binding = binding

    def GetBinding(self):
        return self._binding

    def GetSourceObject(self):
        return self._binding.sourceObject

    def GetBoundObject(self):
        return self._binding.destinationObject

    def GetBoundAttribute(self):
        return self._binding.destinationAttribute

    def SetBoundAttribute(self, attr):
        self._binding.destinationAttribute = attr

    def Patch(self, old, new):
        if self.GetBoundObject() == old:
            self._binding.destinationObject = new
            return True
        return False

    def IsDestination(self):
        return True

    def IsSource(self):
        return False


class ExternalParameterLink(ObjectLink):

    def __init__(self, binding):
        self._binding = binding

    def GetBinding(self):
        return self._binding

    def GetBoundObject(self):
        return self._binding.destinationObject

    def GetBoundAttribute(self):
        return self._binding.destinationAttribute

    def IsDestination(self):
        return True

    def IsSource(self):
        return True


class ValidationContext(object):

    def __init__(self, rootObject, rules):
        self.errors = []
        self.root = rootObject
        self._rules = rules
        self._arguments = {}
        self._stack = []
        self._skipObjects = []
        self._stackStrs = ['root']
        self._destinationBindings = None
        self._sourceBindings = None
        self._allBindings = None
        self._currentRule = None
        self.cache = {}
        self._attributeFilter = ValidationAttributeFilter

    def GetStack(self):
        return self._stack

    def GetStackAsStr(self):
        return '.'.join(self._stackStrs)

    def GetTop(self):
        return self._stack[-1]

    def GetArgument(self, argumentType):
        return self._arguments[argumentType]

    def Walk(self, obj, callback, seen):
        try:
            hash(obj)
            key = obj
        except TypeError:
            key = id(obj)

        if key in seen:
            return
        seen.add(key)
        self._stack.append(obj)
        try:
            callback()
            if isinstance(obj, list) or getattr(obj, '__bluetype__', '') == 'blue.List':
                for i, each in enumerate(obj):
                    if each in self._skipObjects:
                        continue
                    self._stackStrs.append(str(i))
                    self.Walk(each, callback, seen)
                    self._stackStrs.pop()

            else:
                for each in dir(obj):
                    member = getattr(obj, each)
                    if each.startswith('_') or callable(member):
                        continue
                    if isinstance(member, (int,
                     float,
                     long,
                     str,
                     unicode)):
                        continue
                    if member in self._skipObjects:
                        continue
                    if isinstance(member, tuple) and all((isinstance(x, (int,
                     float,
                     long,
                     str,
                     unicode)) for x in member)):
                        continue
                    if self._attributeFilter and not self._attributeFilter(obj, each):
                        continue
                    self._stackStrs.append(each)
                    self.Walk(member, callback, seen)
                    self._stackStrs.pop()

        finally:
            self._stack.pop()

    def GetArguments(self):
        args = set()
        rulesWithArguments = [ x for x in map(lambda r: (r, r.GetArguments()), self._rules) if x[1] ]
        ruleMap = {}

        def inner():
            t = type(self._stack[-1])
            if t not in ruleMap:
                ruleMap[t] = [ x for x in rulesWithArguments if x[0].CanApplyToTypeOf(self._stack[-1]) ]
            for each in ruleMap[t]:
                if each[0].Applies(self):
                    args.update(each[1])

        self.Walk(self.root, inner, set())
        return args

    def Validate(self, arguments):
        self.errors = []
        self.cache = {}
        self._arguments = arguments
        self._destinationBindings = None
        self._sourceBindings = None
        self._allBindings = None
        self._currentRule = None
        self._ruleMap = {}

        def inner():
            validated = False
            t = type(self._stack[-1])
            if t not in self._ruleMap:
                self._ruleMap[t] = [ x for x in self._rules if x.CanApplyToTypeOf(self._stack[-1]) ]
            for each in self._ruleMap[t]:
                self._currentRule = each
                try:
                    validated = each.Apply(self) or validated
                except BaseException:
                    import traceback
                    self.Error(each, 'Exception in the rule:\n\n' + traceback.format_exc())

            time.sleep(0)

        self.Walk(self.root, inner, set())
        self._currentRule = None

    def SkipObject(self, obj):
        self._skipObjects.append(obj)

    def AddError(self, error):
        if error.rule is None:
            error.rule = self._currentRule
        self.errors.append(error)

    def Error(self, obj, message, actions = ()):
        self.AddError(SingleObjectValidationError(obj, message, actions))

    def Expect(self, obj, attribute, rule, message = None, actions = ()):
        try:
            objectToValidate = GetObjectAttribute(obj, attribute)
            if objectToValidate is None:
                return
            rule(objectToValidate, message)
        except AssertionError as e:
            self.AddError(SingleObjectValidationError(obj, '%s %s' % (attribute, str(e)), actions))
        except MultipleValidationErrors as e:
            for error in e.errors:
                self.AddError(error)

    def ExpectValue(self, obj, value, rule, message = None, actions = ()):
        try:
            rule(value, message)
        except AssertionError as e:
            self.AddError(SingleObjectValidationError(obj, '%s %s' % (value, str(e)), actions))
        except MultipleValidationErrors as e:
            for error in e.errors:
                self.AddError(error)

    def ExpectAny(self, obj, attribute, rule, message):
        objectToValidate = GetObjectAttribute(obj, attribute)
        if objectToValidate is None:
            return
        for each in objectToValidate:
            try:
                rule(each, message)
                return
            except AssertionError:
                pass
            except MultipleValidationErrors:
                pass

        self.AddError(SingleObjectValidationError(obj, '%s %s' % (attribute, message)))

    def GetAllObjectBindings(self):
        bindings = blue.FindInterface(self.root, 'TriValueBinding')
        allBindings = [ SourceBindingLink(x) for x in bindings ]
        allBindings.extend((DestinationBindingLink(x) for x in bindings))
        allBindings.extend((SourceDynamicBindingLink(x) for x in blue.FindInterface(self.root, 'Tr2DynamicBinding')))
        allBindings.extend((ExternalParameterLink(x) for x in blue.FindInterface(self.root, 'Tr2ExternalParameter')))
        controllerActions = {}
        for controller in blue.FindInterface(self.root, 'Tr2Controller'):
            controllerActions[controller] = []
            for stateMachine in controller.stateMachines:
                for state in stateMachine.states:
                    controllerActions[controller].extend(state.actions)

        actions = blue.FindInterface(self.root, 'Tr2ActionSetValue')
        actions.extend(blue.FindInterface(self.root, 'Tr2ActionAnimateValue'))
        for a in actions:
            for key, val in controllerActions.iteritems():
                if a in val:
                    allBindings.append(ControllerActionLink(a, key))
                    break

        return allBindings

    def RemoveBinding(self, binding):
        toRemove = None
        if binding and self._allBindings:
            for each in self._allBindings:
                if binding == each.GetBinding():
                    toRemove = each
                    break

        if toRemove:
            if self._destinationBindings:
                cleanupKey = None
                cleanupName = None
                for key, each in self._destinationBindings.iteritems():
                    for name, val in each.iteritems():
                        if toRemove in val:
                            val.remove(toRemove)
                            cleanupKey = key
                            cleanupName = name
                            break

                if cleanupKey and cleanupName:
                    if len(self._destinationBindings[cleanupKey][cleanupName]) == 0:
                        self._destinationBindings[cleanupKey].pop(cleanupName)
                    if len(self._destinationBindings[cleanupKey]) == 0:
                        self._destinationBindings.pop(cleanupKey)
            if self._sourceBindings:
                cleanupKey = None
                cleanupName = None
                for key, each in self._sourceBindings.iteritems():
                    for name, val in each.iteritems():
                        if toRemove in val:
                            val.remove(toRemove)
                            cleanupKey = key
                            cleanupName = name
                            break

                if cleanupKey and cleanupName:
                    if len(self._sourceBindings[cleanupKey][cleanupName]) == 0:
                        self._sourceBindings[cleanupKey].pop(cleanupName)
                    if len(self._sourceBindings[cleanupKey]) == 0:
                        self._sourceBindings.pop(cleanupKey)
            self._allBindings.remove(toRemove)

    def GetBindings(self):
        if self._allBindings is None:
            self._allBindings = self.GetAllObjectBindings()
        return self._allBindings

    def GetDestinationBindings(self):
        if self._destinationBindings is None:
            allBindings = self.GetBindings()
            self._destinationBindings = {}
            for binding in allBindings:
                if binding.IsDestination():
                    self._destinationBindings.setdefault(binding.GetBoundObject(), {}).setdefault(binding.GetBoundAttribute(), []).append(binding)

        return self._destinationBindings

    def GetSourceBindings(self):
        if self._sourceBindings is None:
            allBindings = self.GetBindings()
            self._sourceBindings = {}
            for binding in allBindings:
                if binding.IsSource():
                    self._sourceBindings.setdefault(binding.GetBoundObject(), {}).setdefault(binding.GetBoundAttribute(), []).append(binding)

        return self._sourceBindings

    def IsBoundAsDestination(self, obj, attribute = None):
        if obj.name == 'FresnelFactors':
            pass
        return self._IsBound(obj, attribute, self.GetDestinationBindings())

    def IsBoundAsSource(self, obj, attribute = None):
        return self._IsBound(obj, attribute, self.GetSourceBindings())

    def _IsBound(self, obj, attribute, bindings):
        if attribute is None:
            return obj in bindings
        else:
            boundAttributes = bindings.get(obj, {})
            attributeIsBound = attribute in boundAttributes
            if not attributeIsBound:
                for boundAttribute in boundAttributes:
                    if boundAttribute.startswith(attribute + '.'):
                        return True

            return attributeIsBound


def FindRules(path = None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'validators')
    rules = []
    for root, dirs, files in os.walk(path):
        if root.lower().endswith('test'):
            continue
        for each in files:
            rules.extend(FindRulesInFile(os.path.join(root, each)))

    return rules


def FindRulesInFile(filePath):
    rules = []
    root = os.path.dirname(filePath)
    file = os.path.basename(filePath)
    if file.lower().endswith('.py'):
        sys.path.insert(0, root)
        try:
            module = __import__(os.path.splitext(file)[0])
            for name in dir(module):
                member = getattr(module, name)
                if isinstance(member, BaseValidationRule):
                    if member.name is None:
                        member.name = '%s.%s' % (os.path.splitext(file)[0], name)
                    rules.append(member)

        finally:
            del sys.path[0]

    return rules


def InitializeArgumentsFromFilePath(argumentClasses, path, root):
    return {k:k.CreateFromPath(path, root) for k in argumentClasses}
