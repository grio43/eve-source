#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\generate\process_types.py
import os
import copy
import blue
from iconrendering2.icongenerator import Options, IconGenerator, InputType
from iconrendering2.const import IconStyle, Language
from iconrendering2.imageserver.utils import GetFolder

def GenerateVariationsForTypeIDs(outputFolder, typeIDs, resourceMapper, sofFactory, logger):
    typesFolder = GetFolder(outputFolder, 'TypeIDs')
    mapping = {}

    def _AddToMap(id, type, path):
        if id not in mapping:
            mapping[id] = {}
        mapping[id][type] = os.path.relpath(path, outputFolder)

    def _RenderCallback(typeID, outputInfos):
        for info in outputInfos:
            if info.language == Language.ENGLISH:
                if info.style == IconStyle.STANDARD:
                    if info.size == 512:
                        _AddToMap(typeID, 'render', info.outputPath)
                    else:
                        _AddToMap(typeID, 'icon', info.outputPath)
                if info.style == IconStyle.BP_ORIGINAL:
                    _AddToMap(typeID, 'bp', info.outputPath)
                if info.style == IconStyle.BP_COPY:
                    _AddToMap(typeID, 'bpc', info.outputPath)
                if info.style == IconStyle.BP_REACTION:
                    _AddToMap(typeID, 'reaction', info.outputPath)
                if info.style == IconStyle.BP_RELIC:
                    _AddToMap(typeID, 'relic', info.outputPath)
                if info.style == IconStyle.BP_DUST:
                    _AddToMap(typeID, 'dust', info.outputPath)

    iconGenerator = IconGenerator(resourceMapper=resourceMapper, sofFactory=sofFactory, language=Language.ENGLISH, options=Options.ONLY_USE_EXISTING_BASE_ICONS, postRenderCallback=_RenderCallback)
    errorList = []
    failedTypeIDs = []
    for typeID in typeIDs:
        errors = iconGenerator.Generate(InputType.TYPE_ID, typeID, typesFolder, desiredStyles=IconStyle.STANDARD | IconStyle.ALL_BP, desiredSizes=[64, 512])
        if len(errors) > 0:
            errorList.extend(errors)
            failedTypeIDs.append(typeID)

    blue.resMan.Wait()
    for i in mapping:
        for each in mapping[i].itervalues():
            if not os.path.exists(os.path.join(outputFolder, each)):
                errorList.append('Icon %s not found for typeID %s. The graphicID or iconID is most likely missing backgrounds or foregrounds information in FSD.' % (each, i))

    zhMapping = copy.deepcopy(mapping)
    for typeID, info in mapping.iteritems():
        for key, val in info.iteritems():
            zhVal = os.path.join(os.path.dirname(val), '%s.zh%s' % os.path.splitext(os.path.basename(val)))
            if os.path.exists(os.path.join(outputFolder, zhVal)):
                zhMapping[typeID][key] = zhVal

    return (mapping, zhMapping, errorList)
