#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\errors.py


class ValidationException(RuntimeError):
    MESSAGE = 'Validation failed'

    def __init__(self):
        super(ValidationException, self).__init__(self.MESSAGE)


class SlotConfigurationUnavailable(ValidationException):
    MESSAGE = 'Invalid layout. Slot configuration is not defined.'


class ComponentsUnavailable(ValidationException):
    MESSAGE = 'Invalid layout. Components are not defined.'


class SlotDataUnavailable(ValidationException):
    MESSAGE = 'Invalid layout. Slot data is not available.'


class InvalidBlendMode(ValidationException):
    MESSAGE = 'Invalid layout. Blend mode is invalid.'


class MissingPatternColor(ValidationException):
    MESSAGE = "Invalid layout. A pattern doesn't have a color associated with it."


class UnusedComponentsFitted(ValidationException):
    MESSAGE = 'Invalid layout. Components are fitted into unused slots.'


class ComponentDataUnavailable(ValidationException):
    MESSAGE = 'Invalid component. Component data is not available.'


class ComponentNotAllowedInSlot(ValidationException):
    MESSAGE = 'Component is not allowed in slot.'


class SlotDisallowedForComponent(ValidationException):
    MESSAGE = 'Slot is disallowed for component.'


class ComponentLicensesUnavailable(ValidationException):
    MESSAGE = 'Component licenses do not match valid licenses'


class ComponentLicensesInsufficient(ValidationException):
    MESSAGE = 'Component licenses are not enough for design'
