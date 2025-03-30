#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\validation\utils.py
import glob
import os
import yaml
from caching import Memoize
from fsd import AbsJoin, GetBranchRoot
from fsd.common.fsdYamlExtensions import FsdYamlLoader
STATIC_DATA_ROOT = AbsJoin(GetBranchRoot(), 'eve', 'staticData')

class ValidationError(Exception):
    pass


def Validation(path):
    from platformtools.compatibility.exposure.fsdvalidation import validation as _validation
    return _validation(path)


def Validate(dataByPath):
    from platformtools.compatibility.exposure.fsdvalidation import validate as _validate
    return _validate(dataByPath)


def GetRegisteredCfsdSchemas():
    from platformtools.compatibility.exposure.fsdvalidation import get_registered_cfsd_schemas
    return get_registered_cfsd_schemas()


def GetRegisteredFsdSchemas():
    from platformtools.compatibility.exposure.fsdvalidation import get_registered_fsd_schemas
    return get_registered_fsd_schemas()


def ReadYaml(path):
    if not os.path.exists(path):
        return
    with open(path, 'r') as fd:
        return yaml.load(fd, Loader=FsdYamlLoader)


@Memoize
def GetCFSDSchemaFilePath(schemaName):
    if not schemaName.endswith('.fsdschema'):
        fileName = '{}.fsdschema'.format(schemaName)
    else:
        fileName = schemaName
    for root, folders, files in os.walk(STATIC_DATA_ROOT):
        for f in files:
            if f == fileName:
                return os.path.join(root, fileName)

    raise RuntimeError('Unable to find cfsd schema for {}'.format(schemaName))


@Memoize
def GetCFSDSchema(schemaName):
    filePath = GetCFSDSchemaFilePath(schemaName)
    return ReadYaml(filePath)


def GetCFSDData(schemaName):
    schema = GetCFSDSchema(schemaName)
    schemaPath = GetCFSDSchemaFilePath(schemaName)
    dataRoot = os.path.abspath(os.path.join(os.path.dirname(schemaPath), schema['data'].get('root', '.')))
    _filter = schema['data']['fileFilter']
    data = {}
    for filename in glob.glob(os.path.join(dataRoot, _filter)):
        data[filename] = ReadYaml(filename)

    return data


def GetCFSDEntry(schemaName, _id):
    schema = GetCFSDSchema(schemaName)
    schemaPath = GetCFSDSchemaFilePath(schemaName)
    dataRoot = os.path.abspath(os.path.join(os.path.dirname(schemaPath), schema['data'].get('root', '.')))
    _filter = schema['data']['fileFilter']
    if _filter == '*.staticdata':
        data = ReadYaml(os.path.join(dataRoot, '{}.staticdata'.format(_id)))
    else:
        data = {}
        for filename in glob.glob(os.path.join(dataRoot, _filter)):
            data.update(ReadYaml(filename))

    return data[_id]


def GetTypeData(typeID):
    return GetCFSDEntry('types', typeID)
