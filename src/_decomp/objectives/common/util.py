#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\common\util.py


def fix_fsd_value(value):
    if hasattr(value, 'iteritems'):
        return {key:fix_fsd_value(val) for key, val in value.iteritems()}
    if hasattr(value, '__len__') and not isinstance(value, basestring):
        return [ fix_fsd_value(val) for val in value ]
    return value


def value_as_set(value):
    if value and not isinstance(value, list):
        return set([value])
    else:
        return set(value or [])
