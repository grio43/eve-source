#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\schemas\binaryLoader.py
import cPickle
import ctypes
import persistence
import struct
import loaders
import loaders.objectLoader
import loaders.dictLoader
import loaders.listLoader
import logging
import os
from eveprefs import boot
from path import FsdDataPathObject
from fsd.schemas.telemetryMarkup import TelemetryContext
uint32 = struct.Struct('I')
log = logging.getLogger(__name__)
defaultLoaderFactories = {'float': loaders.FloatFromBinaryString,
 'vector4': loaders.Vector4FromBinaryString,
 'color': loaders.Vector4FromBinaryString,
 'vector3': loaders.Vector3FromBinaryString,
 'vector2': loaders.Vector2FromBinaryString,
 'string': loaders.StringFromBinaryString,
 'resPath': loaders.StringFromBinaryString,
 'enum': loaders.EnumFromBinaryString,
 'bool': loaders.BoolFromBinaryString,
 'int': loaders.IntFromBinaryString,
 'typeID': loaders.IntFromBinaryString,
 'localizationID': loaders.IntFromBinaryString,
 'union': loaders.UnionFromBinaryString,
 'list': loaders.listLoader.ListFromBinaryString,
 'object': loaders.objectLoader.ObjectLoader,
 'dict': loaders.dictLoader.DictLoader,
 'unicode': loaders.UnicodeStringFromBinaryString,
 'npcTag': loaders.IntFromBinaryString,
 'deploymentType': loaders.IntFromBinaryString,
 'npcEnemyFleetTypeID': loaders.IntFromBinaryString,
 'groupBehaviorTreeID': loaders.IntFromBinaryString,
 'npcCorporationID': loaders.IntFromBinaryString,
 'spawnTableID': loaders.IntFromBinaryString,
 'npcFleetCounterTableID': loaders.IntFromBinaryString,
 'dungeonID': loaders.IntFromBinaryString,
 'typeListID': loaders.IntFromBinaryString,
 'npcFleetTypeID': loaders.IntFromBinaryString,
 'metaGroupID': loaders.IntFromBinaryString,
 'fsdReference': loaders.IntFromBinaryString,
 'raceID': loaders.IntFromBinaryString,
 'marketGroupID': loaders.IntFromBinaryString,
 'ShipGroupID': loaders.IntFromBinaryString,
 'certificateTemplateID': loaders.IntFromBinaryString,
 'factionID': loaders.IntFromBinaryString}

def sizeof_fmt(num):
    for x in [' bytes',
     ' KB',
     ' MB',
     ' GB']:
        if num < 1024.0 and num > -1024.0:
            return '%3.1f%s' % (num, x)
        num /= 1024.0

    return '%3.1f%s' % (num, ' TB')


class LoaderState(object):

    def __init__(self, factories, logger = None, cfgObject = None):
        self.factories = factories

    def RepresentSchemaNode(self, data, offset, path, schemaNode):
        schemaType = schemaNode.get('type')
        if schemaType in self.factories:
            return self.factories[schemaType](data, offset, schemaNode, path, self)
        raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))

    def FormatSize(self, size):
        return sizeof_fmt(size)


def RepresentSchemaNode(data, offset, schemaNode, path, extraState = None):
    schemaType = schemaNode.get('type')
    if extraState is None:
        extraState = LoaderState(defaultLoaderFactories, None)
    if schemaType in extraState.factories:
        return extraState.factories[schemaType](data, offset, schemaNode, path, extraState)
    raise NotImplementedError("Unknown type not supported in binary loader '%s'" % str(schemaType))


def LoadFromString(dataString, optimizedSchema = None, path = None, extraState = None):
    if path is None:
        path = FsdDataPathObject('<string input>')
    offsetToData = 0
    if optimizedSchema is None:
        schemaSize = uint32.unpack_from(dataString, 0)[0]
        optimizedSchema = cPickle.loads(dataString[4:schemaSize + 4])
        offsetToData = schemaSize + 4
    dataBuffer = ctypes.create_string_buffer(dataString, len(dataString))
    return RepresentSchemaNode(dataBuffer, offsetToData, optimizedSchema, path, extraState)


def GetEmbeddedSchemaAndSizeFromFile(fileObject):
    schemaSize = uint32.unpack(fileObject.read(4))[0]
    pickledSchema = fileObject.read(schemaSize)
    return (cPickle.loads(pickledSchema), schemaSize)


def LoadIndexFromFile(fileObject, optimizedSchema = None, cacheItems = 100, path = None, extraState = None):
    if extraState is None:
        extraState = LoaderState(defaultLoaderFactories, None)
    if path is None:
        path = FsdDataPathObject('<file input>')
    offsetToData = 0
    if optimizedSchema is None:
        fileObject.seek(0)
        optimizedSchema, schemaSize = GetEmbeddedSchemaAndSizeFromFile(fileObject)
        offsetToData = schemaSize + 4
    if optimizedSchema.get('multiIndex', False):
        return loaders.dictLoader.MultiIndexLoader(fileObject, cacheItems, optimizedSchema, path, extraState, offsetToData=offsetToData)
    else:
        return loaders.dictLoader.IndexLoader(fileObject, cacheItems, optimizedSchema, path, extraState, offsetToData=offsetToData)


class BlueResFileIOWrapper(object):

    def __init__(self, resFile):
        self.__resFile__ = resFile

    def seek(self, offset, start = None):
        if start is None:
            return self.__resFile__.seek(offset)
        else:
            if start == os.SEEK_END:
                offset = -offset
            return self.__resFile__.seek(offset, start)

    def read(self, bytes):
        with TelemetryContext('FSD File Read'):
            return self.__resFile__.Read(bytes)

    def tell(self):
        return self.__resFile__.pos


def LoadFSDDataForCFG(dataResPath, schemaResPath = None, optimize = True, cacheSize = 100):
    import blue
    import schemaOptimizer
    res = blue.ResFile()
    if schemaResPath is not None:
        if not res.Open(schemaResPath):
            log.error('Could not load FSD data schema: %s', schemaResPath)
        else:
            schema = persistence.LoadSchema(res.Read())
            if optimize:
                schema = persistence.GetUnOptimizedRuntimeSchema(schema)
                schema = schemaOptimizer.OptimizeSchema(schema, boot.role.capitalize())
    else:
        schema = None
    if not res.Open(dataResPath):
        log.error('Could not load FSD data file: %s', dataResPath)
    else:
        wrappedRes = BlueResFileIOWrapper(res)
        if schema is None:
            peekSchema, size = GetEmbeddedSchemaAndSizeFromFile(wrappedRes)
            wrappedRes.seek(0)
        else:
            peekSchema = schema
        if peekSchema['type'] == 'dict' and peekSchema.get('buildIndex', False):
            return LoadIndexFromFile(wrappedRes, schema, cacheSize, path=FsdDataPathObject('<file %s>' % dataResPath))
        s = res.Read()
        log.info('Loading FSD data file %s into memory. %s', dataResPath, sizeof_fmt(len(s)))
        return LoadFromString(s, schema, path=FsdDataPathObject('<file %s>' % dataResPath))


def LoadFSDDataInPython(dataResPath, schemaResPath = None, optimize = None, cacheSize = 100):
    import schemaOptimizer
    if schemaResPath is not None:
        with open(schemaResPath, 'r') as schemaFile:
            schema = persistence.LoadSchema(schemaFile.read())
            if optimize:
                schema = persistence.GetUnOptimizedRuntimeSchema(schema)
                schema = schemaOptimizer.OptimizeSchema(schema, optimize)
    else:
        schema = None
    dataFile = open(dataResPath, 'rb')
    if schema is None:
        peekSchema, size = GetEmbeddedSchemaAndSizeFromFile(dataFile)
        dataFile.seek(0)
    else:
        peekSchema = schema
    if peekSchema['type'] == 'dict' and peekSchema.get('buildIndex', False):
        return LoadIndexFromFile(dataFile, schema, cacheSize, path=FsdDataPathObject('<file %s>' % dataResPath))
    else:
        s = dataFile.read()
        log.info('Loading FSD data file %s into memory. %s', dataResPath, sizeof_fmt(len(s)))
        dataFile.close()
        return LoadFromString(s, schema, path=FsdDataPathObject('<file %s>' % dataResPath))


def LoadFSDDataForCFGOrFail(dataResPath, schemaResPath = None, optimize = True, cacheSize = 100):
    data = LoadFSDDataForCFG(dataResPath, schemaResPath, optimize, cacheSize)
    if data is None:
        errorString = 'Could not load FSD data for {dataResPath}'.format(dataResPath=dataResPath)
        raise RuntimeError(errorString)
    return data
