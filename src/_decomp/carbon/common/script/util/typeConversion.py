#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\typeConversion.py
conversionTable = {'int': int,
 'float': float,
 'str': str,
 'unicode': unicode}

class ConvertVariableException(Exception):
    pass


def CastValue(type, value):
    if type in conversionTable:
        return conversionTable[type](value)
    raise ConvertVariableException, 'Unknown conversion type -%s-' % type
