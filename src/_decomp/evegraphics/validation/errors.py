#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\errors.py
ERROR_MESSAGE_INVALID_RED_FILE = 'has invalid redFile'
ERROR_MESSAGE_LIST_IS_EMPTY = 'is empty'
ERROR_MESSAGE_HAVE_THE_SAME_NAME = 'have the same name'
ERROR_MESSAGE_ITEMS_ARE_EQUAL = 'are equal'
ERROR_MESSAGE_PRIMITIVE_COUNT_TOO_HIGH = 'The primitive count is too damn high'

def GetTypeName(o):
    try:
        return o.__typename__
    except AttributeError:
        return o.__class__.__name__


class ValidationError(Exception):

    def __init__(self, erroneousObjects, errorMessage, actions = (), rule = None):
        self.errorMessage = errorMessage
        self.errorObjects = erroneousObjects
        self.actions = actions
        self.rule = rule

    def GetErrorMessage(self):
        return str(self)

    def GetErrorObjects(self):
        return self.errorObjects

    def GetRuleName(self):
        return self.rule.name or 'UnknownRule'

    def __str__(self):
        raise NotImplementedError()


class SingleObjectValidationError(ValidationError):

    def __init__(self, erroneousObject, errorMessage, actions = ()):
        super(SingleObjectValidationError, self).__init__([erroneousObject], errorMessage, actions)

    def __str__(self):
        errorObject = self.GetErrorObjects()[0]
        name = getattr(errorObject, 'name', '')
        if name:
            return "%s '%s': %s" % (GetTypeName(errorObject), name, self.errorMessage)
        else:
            return '%s: %s' % (GetTypeName(errorObject), self.errorMessage)


class MultipleObjectValidationError(ValidationError):

    def __init__(self, erroneousObjects, errorMessage, actions = ()):
        super(MultipleObjectValidationError, self).__init__(erroneousObjects, errorMessage, actions)

    def __str__(self):
        names = [ getattr(o, 'name', '') for o in self.GetErrorObjects() ]
        typeName = GetTypeName(self.GetErrorObjects()[0])
        return '%s %s %s: %s' % (len(names),
         typeName,
         ','.join([ '%s' % name for name in set(names) ]),
         self.errorMessage)


class MultipleValidationErrors(Exception):

    def __init__(self, errors):
        self.errors = errors
