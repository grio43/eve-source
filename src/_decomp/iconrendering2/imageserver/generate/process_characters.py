#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\generate\process_characters.py
import os
import blue
import osutils
import copy
from iconrendering2.imageserver.utils import CopyFile, GetFolder

def GenerateCharacterIcons(outputFolder):
    charactersFolder = GetFolder(outputFolder, 'Characters')
    inputFolder = blue.paths.ResolvePath('res:/UI/Texture/StorylinePortraits')
    mapping = {}
    errorList = []

    def _AddToMap(id, path):
        if not os.path.exists(path):
            errorList.append('Icon %s not found for characterID %s.' % (path, id))
        else:
            mapping[str(id)] = str(os.path.relpath(path, outputFolder))

    for file in osutils.FindFiles(inputFolder):
        baseName = os.path.basename(file)
        destPath = os.path.join(charactersFolder, baseName)
        CopyFile(file, destPath)
        _AddToMap(os.path.splitext(baseName)[0], destPath)

    zhMapping = copy.deepcopy(mapping)
    return (mapping, zhMapping, errorList)
