#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\mapReduce\defaultWalker.py
import os
import tempfile
import errno
from uuid import uuid4

def ListSubDirs(path):
    for directoryContent in os.listdir(path):
        if os.path.isdir(os.path.join(path, directoryContent)):
            yield directoryContent


def ListFilesInDir(path):
    for directoryContent in os.listdir(path):
        if os.path.isfile(os.path.join(path, directoryContent)):
            yield directoryContent


class FileLoadingException(Exception):
    pass


class MapReduceDirectoryWalker(object):

    def __init__(self, rootPath, fileLoader, tempPath):
        self.rootPath = rootPath
        self.fileLoader = fileLoader
        randomer_temp = os.path.join(tempPath, str(uuid4()))
        if not os.path.exists(randomer_temp):
            try:
                os.makedirs(randomer_temp)
            except os.error as err:
                if err.errno != errno.EEXIST:
                    raise

        self.tempPath = randomer_temp
        self.openTemporaryFiles = {}
        self.temporaryFiles = {}

    def GetRoot(self):
        return self.rootPath

    def GetFilesInDirectory(self, absolutePath):
        return ListFilesInDir(absolutePath)

    def GetSubDirectories(self, absolutePath):
        return ListSubDirs(absolutePath)

    def GetFileContents(self, absolutePath):
        with open(absolutePath, 'r') as f:
            try:
                return self.fileLoader(f)
            except Exception as e:
                raise FileLoadingException(str(e))

    def GetTemporaryFileForWriting(self, filename, mode):
        fullpath = os.path.join(self.tempPath, filename)
        if not os.path.exists(os.path.dirname(fullpath)):
            try:
                os.makedirs(os.path.dirname(fullpath))
            except os.error as err:
                if err.errno != errno.EEXIST:
                    raise

        f = open(fullpath, 'wb')
        self.openTemporaryFiles[filename] = f
        return f

    def CloseTemporaryWriteFiles(self):
        for i, v in self.openTemporaryFiles.iteritems():
            self.temporaryFiles[i] = v.close()

        self.openTemporaryFiles = {}

    def OpenTemporaryFileForReading(self, filename):
        return open(os.path.join(self.tempPath, filename), 'rb')

    def IsFolderIncluded(self, directoryFileContents):
        return True
