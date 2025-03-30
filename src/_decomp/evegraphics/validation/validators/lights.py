#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\lights.py
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.validationFunctions import ValidateResPath

@Validate('Tr2Light')
def ValidateLightProfilePath(context, light):
    if getattr(light, 'lightProfilePath'):
        ValidateResPath(context, light, 'lightProfilePath', extensions=('.dds', '.ies'))
