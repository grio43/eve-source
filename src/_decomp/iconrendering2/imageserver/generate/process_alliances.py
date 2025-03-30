#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\generate\process_alliances.py
import os
import blue
import osutils
from iconrendering2.imageserver.utils import CopyFile, GetFolder

def GeneratePlayerAllianceIcons(rootInputFolder, rootOutputFolder):
    errorList = []
    mappings = {}

    def _AddToMap(dict, id, path):
        if not os.path.exists(path):
            if not os.path.exists(path):
                errorList.append('Icon %s not found for allianceID %s.' % (path, id))
        elif id in dict:
            errorList.append('Found two different icons for allianceID %s' % id)
        else:
            dict[str(id)] = str(os.path.relpath(path, rootOutputFolder))

    for server in ['TQ', 'SR']:
        mapping = {}
        if rootInputFolder:
            inputFolder = os.path.join(rootInputFolder, server)
            outputFolder = GetFolder(rootOutputFolder, 'PlayerAlliances-%s' % server)
            defaultAllianceFile = os.path.join(blue.paths.ResolvePath('res:/UI/Texture/Alliance'), '1_128_1.png')
            defaultAllianceDestFile = os.path.join(outputFolder, 'default.png')
            CopyFile(defaultAllianceFile, defaultAllianceDestFile)
            _AddToMap(mapping, 0, defaultAllianceDestFile)
            for file in osutils.FindFiles(inputFolder):
                baseName = os.path.basename(file)
                destPath = os.path.join(outputFolder, baseName)
                CopyFile(file, destPath)
                _AddToMap(mapping, os.path.splitext(baseName)[0], destPath)

        mappings[server] = mapping

    return (mappings['TQ'], mappings['SR'], errorList)
