#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdUtilities\loaders.py
import re
import time
import os
import yaml
from fsd.mapReduce import MapReduceMany, defaultWalker
from fsd.common.pathSpecifiers import PathConditional, GetPathSpecifierRegex
from fsd.mapReduce.operations import MapReduceFinalizeJob, MapOperation
from fsd.schemas.binaryLoader import LoadFromString
from fsd.schemas.binaryRepresenter import RepresentAsBinaryWithEmbeddedSchema
from fsd.schemas.schemaOptimizer import OptimizeSchema
from fsd.schemas.persistence import SafeSchemaLoader
from fsdUtilities.pathUtils import GetStaticDataPath, GetAbsoluteBranchPath
from fsd import AbsJoin
from brennivin.yamlext import loadfile

def LoadSchema(schemaPath):
    if '#' in schemaPath:
        filePath, schemaPath = schemaPath.split('#')
    else:
        filePath, schemaPath = schemaPath, ''
    if os.path.exists(GetStaticDataPath(filePath)):
        filePath = GetStaticDataPath(filePath)
    with open(filePath, 'r') as schemaFile:
        data = yaml.load(schemaFile, Loader=SafeSchemaLoader)
    for part in schemaPath.split('.'):
        if part:
            data = data[part]

    return data


def LoadDataFromFile(filePath):
    if os.path.exists(GetStaticDataPath(filePath)):
        pathToFile = GetStaticDataPath(filePath)
    else:
        pathToFile = filePath
    return loadfile(pathToFile)


def _MapData(rootPath, relativePath, filesInHeirachy, fileContent):
    yield (relativePath, fileContent)


def _FinalizeData(rootPath, results):
    return {path:content for path, content in results}


def LoadDataFromMultipleFiles(root, includePath, showLog = True):
    if os.path.exists(GetStaticDataPath(root)):
        pathToRoot = GetStaticDataPath(root)
    else:
        pathToRoot = root
    pathRegularExpression = GetPathSpecifierRegex(includePath)
    data = {}
    startTime = time.time()
    for root, dirs, files in os.walk(pathToRoot):
        for filePath in files:
            if re.match(pathRegularExpression, filePath):
                dataKey = _RemoveSimilarEndSubstring(filePath, includePath)
                try:
                    dataKey = int(dataKey)
                except ValueError:
                    pass

                data[dataKey] = loadfile(AbsJoin(root, filePath))

    if showLog:
        print 'Parsed %d files in %.1f sec for %s' % (len(data), time.time() - startTime, GetAbsoluteBranchPath(root, includePath))
    return data


def LoadDataFromMultipleFilesWithMultiProcessing(root, includePath, mapFunction = _MapData, finalizeFunction = _FinalizeData):
    if os.path.exists(GetStaticDataPath(root)):
        pathToRoot = GetStaticDataPath(root)
    else:
        pathToRoot = root
    includeConditionals = PathConditional(includes=includePath)
    walker = defaultWalker.MapReduceDirectoryWalker(pathToRoot, loadfile, GetAbsoluteBranchPath('eve/autobuild/temp/staticData/utilities'))
    reduceFinalizeJob = MapReduceFinalizeJob('objectData', [MapOperation('MapData', mapFunction)], pathConditional=includeConditionals, finalizeFunction=finalizeFunction)
    import multiprocessing
    pool = multiprocessing.Pool(processes=4)
    startTime = time.time()
    generatedResults = MapReduceMany(walker, [], includePath, [], [reduceFinalizeJob], pool)
    generatedResults = generatedResults['objectData']
    filePath = GetAbsoluteBranchPath(root, includePath)
    print 'Parsed %d files in %.1f sec for %s' % (len(generatedResults), time.time() - startTime, filePath)
    result = {}
    for key, value in generatedResults.iteritems():
        shortenedKey = _RemoveSimilarEndSubstring(key, includePath)
        try:
            shortenedKey = int(shortenedKey)
        except ValueError:
            pass

        result[shortenedKey] = value

    return result


def _RemoveSimilarEndSubstring(key, path):
    reversedPath = path[::-1]
    reversedKey = key[::-1]
    index = 0
    while len(reversedKey) != 0 and index < len(reversedPath) and reversedKey[0] == reversedPath[index]:
        reversedKey = reversedKey[1:]
        index = index + 1

    return reversedKey[::-1]


def CreateFsdObjectFromData(data, schema, target = 'client'):
    schema = LoadSchema(schema)
    binaryBlob = RepresentAsBinaryWithEmbeddedSchema(data, OptimizeSchema(schema, target))
    return LoadFromString(binaryBlob)
