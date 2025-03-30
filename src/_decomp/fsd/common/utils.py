#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\common\utils.py
from fsd.build.fsdSchemaTypes.intType import Int32, Int64
from fsd.build.fsdSchemaTypes.stringType import String, WString

class FsdPrimitiveTypeError(Exception):
    pass


def get_primitive_py_type(fsd_type, type_factory = None):
    from fsd.build.eveFsdBuilder import EveFsdTypeFactory
    type_factory = type_factory if type_factory is not None else EveFsdTypeFactory()
    if fsd_type == 'dict':
        return dict
    if fsd_type in ('list', 'sortedList', 'uniqueList'):
        return list
    if fsd_type == 'object':
        return object
    if fsd_type in ('idGenerator', 'int', 'fsdReference', 'externalReference', 'long'):
        return int
    if fsd_type == 'float':
        return float
    if fsd_type in ('string', 'unicode', 'resPath', 'enum'):
        return str
    if fsd_type == 'union':
        return str
    if fsd_type == 'bool':
        return bool
    if 'vector' in fsd_type or fsd_type == 'color':
        return list
    if fsd_type in type_factory.__typeRegistry__:
        type_class = type_factory.__typeRegistry__[fsd_type]
        if issubclass(type_class, (Int32, Int64)):
            return int
        if issubclass(type_class, (String, WString)):
            return str
        raise FsdPrimitiveTypeError('Unable to resolve fsd type {} to primitive Python type'.format(fsd_type))
    else:
        raise FsdPrimitiveTypeError('Unable to resolve fsd type {} to primitive Python type'.format(fsd_type))
