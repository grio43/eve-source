#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\generate\process_corps.py
import os
import copy
import osutils
import blue
from eve.client.script.ui.const.eveIconConst import IN_CORP_ICONS, CORP_ICONS, IN_ICONS
from iconrendering2.imageserver.utils import CopyFile, GetFolder

def GenerateCorpAndFactionIcons(outputFolder):
    corpsFolder = GetFolder(outputFolder, 'Corps')
    factionsFolder = GetFolder(outputFolder, 'Factions')
    errorList = []
    corpsDict = {}
    for key, val in CORP_ICONS.iteritems():
        lowerVal = val.lower()
        if lowerVal not in corpsDict:
            corpsDict[lowerVal] = []
        corpsDict[lowerVal].append(key)

    factionsDict = {}
    for key, val in IN_CORP_ICONS.iteritems():
        lowerVal = val.lower()
        if lowerVal not in factionsDict:
            factionsDict[lowerVal] = []
        factionsDict[lowerVal].append(key)

    def _AddToMap(dict, id, path):
        if not os.path.exists(path):
            errorList.append('Icon %s not found for corpID %s.' % (path, id))
        elif id in dict:
            errorList.append('Found two different icons for corpID %s' % id)
        else:
            dict[id] = str(os.path.relpath(path, outputFolder))

    mapping = {}
    inputFolder = blue.paths.ResolvePath('res:/UI/Texture/Corps')
    for file in osutils.FindFiles(inputFolder):
        if '.zh.' in file:
            continue
        factionIds = []
        corpIds = []
        iconBasename = os.path.basename(file)
        iconName, ext = os.path.splitext(iconBasename)
        corpsLocation = os.path.join('res:/UI/Texture/Corps/', iconBasename).lower()
        corpsName = 'corps_%s' % iconName
        if corpsLocation in factionsDict:
            factionIds.extend(factionsDict[corpsLocation])
        elif corpsName in factionsDict:
            factionIds.extend(factionsDict[corpsName])
        elif corpsLocation in corpsDict:
            corpIds.extend(corpsDict[corpsLocation])
        elif corpsName in corpsDict:
            corpIds.extend(corpsDict[corpsName])
        for id in corpIds:
            destFile = os.path.join(corpsFolder, '%s%s' % (id, ext))
            CopyFile(file, destFile)
            _AddToMap(mapping, id, destFile)
            zhFile = os.path.join(os.path.dirname(file), '%s.zh%s' % os.path.splitext(file))
            if os.path.exists(zhFile):
                zhDestFile = os.path.join(corpsFolder, '%s.zh%s' % (id, ext))
                CopyFile(zhFile, zhDestFile)

        for id in factionIds:
            destFile = os.path.join(factionsFolder, '%s%s' % (id, ext))
            CopyFile(file, destFile)
            _AddToMap(mapping, id, destFile)
            zhFile = os.path.join(os.path.dirname(file), '%s.zh%s' % os.path.splitext(file))
            if os.path.exists(zhFile):
                zhDestFile = os.path.join(factionsFolder, '%s.zh%s' % (id, ext))
                CopyFile(zhFile, zhDestFile)

    iconsFolder = blue.paths.ResolvePath('res:/UI/Texture/Icons')
    for key, val in IN_ICONS.iteritems():
        name = val.replace('ui_', '')
        file = os.path.join(iconsFolder, '%s.png' % name)
        destFile = os.path.join(factionsFolder, '%s.png' % key)
        CopyFile(file, destFile)
        _AddToMap(mapping, key, destFile)
        zhFile = os.path.join(iconsFolder, '%s.zh.png' % name)
        if os.path.exists(zhFile):
            zhDestFile = os.path.join(factionsFolder, '%s.zh%s' % os.path.splitext(os.path.basename(destFile)))
            CopyFile(zhFile, zhDestFile)

    defaultCorpFile = os.path.join(inputFolder, '1.png')
    defaultCorpDestFile = os.path.join(corpsFolder, 'default.png')
    CopyFile(defaultCorpFile, defaultCorpDestFile)
    _AddToMap(mapping, 0, defaultCorpDestFile)
    zhMapping = copy.deepcopy(mapping)
    for corpID, path in mapping.iteritems():
        zhVal = os.path.join(os.path.dirname(path), '%s.zh%s' % os.path.splitext(os.path.basename(path)))
        if os.path.exists(os.path.join(outputFolder, zhVal)):
            zhMapping[corpID] = str(zhVal)

    return (mapping, zhMapping, errorList)
