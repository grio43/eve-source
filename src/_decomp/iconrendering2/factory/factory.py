#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\factory\factory.py
import os
import evetypes
import blue
import trinity
import yamlext
import devenv
import fsdauthoringutils
from fsdUtilities.loaders import LoadDataFromFile
from fsdBuiltData.common.graphicIDs import GetGraphicIDDictionary, GetGraphicFile, GetControllerVariableOverrides
from fsdBuiltData.common.iconIDs import GetIcon
from iconrendering2.metadata import AppendControllerOverrides
from iconrendering2.const import Language, IconStyle, InputType, GetSceneForSofRaceFaction
from iconrendering2.const import STYLE_STRINGS, BLUEPRINT_SCENE_GFXID
from iconrendering2.factory.recipe import IconType, TypeData, RenderedIconRecipe, HanddrawnIconRecipe
from iconrendering2.renderers.renderer_base import IconRenderInfo
from iconrendering2.renderers.renderer_fromfile import FromFileIconRenderer
from iconrendering2.renderers.renderer_sun import SunIconRenderer
from iconrendering2.renderers.renderer_planetary_pin import PlanetaryPinIconRenderer
from iconrendering2.renderers.renderer_spaceobject import SpaceObjectIconRenderer
from iconrendering2.renderers.renderer_hologram import HologramIconRenderer

class IconRendererFactory(object):

    def __init__(self, resourceMapper = None, sofFactory = None):
        self._metagroups = LoadDataFromFile('metaGroups/metaGroups.staticdata')
        self._graphicIDs = None
        self._resourceMapper = resourceMapper if resourceMapper else fsdauthoringutils.GraphicsCache(devenv.EVEROOT)
        if not sofFactory:
            self._sofFactory = trinity.EveSOF()
            self._sofFactory.dataMgr.LoadData('res:/dx9/model/spaceobjectfactory/data.red')
            blue.resMan.Wait()
        else:
            self._sofFactory = sofFactory
        self.test = []

    def CreateRenderers(self, inputType, input, outputFolder, desiredStyles, desiredMetagroups, desiredSizes, onlyUseExistingBaseIcons, renderMetagroupOverlay, metadata, language):
        renderers = []
        errors = []
        typeIDs = set()
        if inputType == InputType.RED_FILE:
            typeIDs = self._ConvertRedFileToTypeIDs(input, desiredMetagroups)
        elif inputType == InputType.GRAPHIC_ID:
            typeIDs = self._ConvertGraphicIDToTypeIDs(input, desiredMetagroups)
        elif inputType == InputType.ICON_ID:
            typeIDs = self._ConvertIconIDToTypeIDs(input, desiredMetagroups)
        elif inputType == InputType.TYPE_ID:
            typeIDs.add(input)
        if not typeIDs:
            errors.append('No Type IDs exist for %s' % input)
        for t in typeIDs:
            r, e = self._CreateRenderersForTypeID(t, outputFolder, desiredStyles, desiredSizes, onlyUseExistingBaseIcons, renderMetagroupOverlay, metadata, language)
            e = [ (input, each[1], each[2]) for each in e ]
            renderers.extend(r)
            errors.extend(e)

        _CleanupDuplicateRenderInfos(renderers)
        return (renderers, errors)

    def _CreateRenderersForTypeID(self, typeID, outputFolder, desiredStyles, desiredSizes, onlyUseExistingBaseIcons, renderMetagroupOverlay, metadata, language):
        renderers = []
        errors = []
        typeData = TypeData(typeID, self._resourceMapper)
        if typeData.iconType == IconType.NONE:
            errors.append((typeID, 'Could not determine icon type for typeID %s.' % typeID, ''))
            return (renderers, errors)
        metagroupData = self._metagroups.get(typeData.metagroupID, None)
        metagroupString = metagroupData.get('iconSuffix', None) if metagroupData else None
        metagroupIconID = metagroupData.get('iconID', None) if metagroupData else None
        metagroupOverlayPath = GetIcon(metagroupIconID).iconFile if metagroupIconID else None
        if language == Language.AUTO_DETECT:
            if typeData.isRenderable:
                if typeData.isSof:
                    method = lambda : _LoadForDna(typeData.dna, self._sofFactory)
                else:
                    method = lambda : _LoadForPath(typeData.graphicFile)
                languages = _RunAutoDetectLanguageForRenderedIcon(method)
            else:
                languages = _RunAutoDetectLanguageForHanddrawnIcon(typeData.iconFile)
            for l in languages:
                r, e = self._CreateRenderersForTypeID(typeID, outputFolder, desiredStyles, desiredSizes, onlyUseExistingBaseIcons, renderMetagroupOverlay, metadata, l)
                renderers.extend(r)
                errors.extend(e)

        else:
            recipes = typeData.GetRecipes(onlyUseExistingBaseIcons, renderMetagroupOverlay)
            ffR = FromFileIconRenderer(language)
            sunR = ffR if onlyUseExistingBaseIcons else SunIconRenderer(typeData.graphicFile, language)
            piR = ffR if onlyUseExistingBaseIcons else PlanetaryPinIconRenderer(typeData.graphicFile, language)
            sofR = None
            bpR = None
            holoR = None
            if typeData.dnaParts:
                factionScene = GetSceneForSofRaceFaction(typeData.dnaParts.hull, typeData.dnaParts.faction, typeData.dnaParts.race)
                bpScenePath = GetGraphicFile(BLUEPRINT_SCENE_GFXID)
                sofR = ffR if onlyUseExistingBaseIcons else SpaceObjectIconRenderer(self._sofFactory, factionScene, typeData.dna, language)
                bpR = ffR if onlyUseExistingBaseIcons else SpaceObjectIconRenderer(self._sofFactory, bpScenePath, typeData.dna, language)
                holoR = ffR if onlyUseExistingBaseIcons else HologramIconRenderer(self._sofFactory, typeData.dna, language)

            def _GetRenderer(style):
                if typeData.iconType == IconType.SUN:
                    return sunR
                if typeData.iconType == IconType.PLANETARY_PIN:
                    return piR
                if typeData.iconType in [IconType.SOF_OTHER, IconType.SOF_SHIP_OR_STRUCTURE]:
                    if style == IconStyle.HOLOGRAM:
                        return holoR
                    if style in [IconStyle.TRANSPARENT, IconStyle.STANDARD]:
                        return sofR
                    if style in [IconStyle.BP_ORIGINAL,
                     IconStyle.BP_COPY,
                     IconStyle.BP_RELIC,
                     IconStyle.BP_REACTION,
                     IconStyle.BP_DUST]:
                        return bpR
                else:
                    if typeData.iconType in [IconType.OTHER, IconType.HANDDRAWN]:
                        return ffR
                    return None

            for style, recipe in recipes.iteritems():
                if style & desiredStyles:
                    for s, f in recipe.sizesAndFormats:
                        if s not in desiredSizes:
                            continue
                        renderer = _GetRenderer(style)
                        if not renderer:
                            continue
                        useMetagroup = recipe.useMetagroup and s != 512
                        styleMetadata = _GetMetadataForStyle(metadata, style) if recipe.useMetadata else None
                        if styleMetadata and typeData.graphicID is not None:
                            controllerOverrides = GetControllerVariableOverrides(graphicID=typeData.graphicID)
                            if controllerOverrides is not None:
                                AppendControllerOverrides(styleMetadata, controllerOverrides)
                        inputIcon = None
                        if isinstance(recipe, RenderedIconRecipe):
                            if recipe.useExistingIcons:
                                path, found = _CheckForExistingRenderedBaseIcon(recipe.input, recipe.sourceFolder, f, style, s, None, language, recipe.writeSize)
                                if found:
                                    inputIcon = path
                                else:
                                    continue
                        elif isinstance(recipe, HanddrawnIconRecipe):
                            inputIcon = recipe.sourceIcons.get(s, None)
                            if not inputIcon:
                                continue
                        _AddRenderInfo(renderer, outputFolder, recipe.input, style, recipe.background, recipe.backgroundTransparency, recipe.overlay, metagroupOverlayPath if useMetagroup else None, metagroupString if useMetagroup and not typeData.isSof else None, f, s, language, recipe.outline, styleMetadata, inputIcon, recipe.writeSize)
                        if renderer.HasRenderInfos() and renderer not in renderers:
                            renderers.append(renderer)

        return (renderers, errors)

    def _ConvertGraphicIDToTypeIDs(self, graphicID, desiredMetagroups):
        typeIDs = set()
        for typeID in evetypes.Iterate():
            metagroup = evetypes.GetMetaGroupID(typeID)
            if not metagroup or metagroup in desiredMetagroups:
                gid = evetypes.GetGraphicID(typeID)
                if gid and gid == graphicID:
                    typeIDs.add(typeID)

        return typeIDs

    def _ConvertIconIDToTypeIDs(self, iconID, desiredMetagroups):
        typeIDs = set()
        for typeID in evetypes.Iterate():
            metagroup = evetypes.GetMetaGroupID(typeID)
            if not metagroup or metagroup in desiredMetagroups:
                iid = evetypes.GetIconID(typeID)
                if iid and iid == iconID:
                    typeIDs.add(typeID)

        return typeIDs

    def _ConvertRedFileToTypeIDs(self, redFilePath, desiredMetagroups):
        if self._graphicIDs is None:
            self._graphicIDs = GetGraphicIDDictionary()
        redFilePath = redFilePath.replace('\\', '/')
        resolvedRedFilePath = blue.paths.ResolvePath(redFilePath)
        redFile = yamlext.loadfile(resolvedRedFilePath)
        graphicIDs = self._resourceMapper.GetGraphicIdsForGraphicFile(redFilePath)
        if redFile and 'name' in redFile:
            hullName = redFile['name']
            for graphicID, graphicIDObject in self._graphicIDs.iteritems():
                if graphicID not in graphicIDs:
                    if graphicIDObject.sofHullName == hullName:
                        graphicIDs.append(graphicID)

        typeIDs = set()
        for graphicID in graphicIDs:
            typeIDs = typeIDs.union(typeIDs, self._ConvertGraphicIDToTypeIDs(graphicID, desiredMetagroups))

        return typeIDs


def _AddRenderInfo(renderer, outputFolder, input, style, background, backgroundTransparency, overlay, metagroupOverlay, metagroupString, format, size, language, outline, metadata, inputIcon, writeSize = True):
    iconName = _BuildIconName(input, format, style, size, metagroupString, language, writeSize)
    renderInfo = IconRenderInfo(outputFolder, iconName, size, format)
    renderInfo.background = background
    renderInfo.backgroundTransparent = backgroundTransparency
    renderInfo.overlay = overlay
    renderInfo.foreground = metagroupOverlay
    renderInfo.outlineColor = outline
    renderInfo.metadata = metadata
    renderInfo.inputIcon = inputIcon
    renderInfo.style = style
    renderInfo.language = language
    renderer.AddRenderInfo(renderInfo)


def _GetMetadataForStyle(metadata, style):
    if not metadata:
        return None
    if style & IconStyle.ALL_BP:
        style = IconStyle.STANDARD
    return metadata.get(style, None)


def _BuildIconName(baseName, format, style, size, metagroupString = None, language = Language.ENGLISH, writeSize = True):
    fileName = '%s' % baseName
    if writeSize:
        fileName = '%s_%s' % (fileName, size)
    styleString = STYLE_STRINGS.get(style, None)
    if styleString:
        fileName = '%s_%s' % (fileName, styleString)
    if metagroupString:
        fileName = '%s_%s' % (fileName, metagroupString)
    if language not in [Language.ENGLISH, Language.AUTO_DETECT]:
        fileName = '%s.%s' % (fileName, language)
    outputPath = '%s.%s' % (fileName, format)
    return outputPath


def _CheckForExistingRenderedBaseIcon(graphicID, baseIconFolder, format, style, size, metagroupString, language, writeSize):
    if not baseIconFolder:
        return ('', False)
    iconName = _BuildIconName(graphicID, format, style, size, metagroupString, language, writeSize)
    iconPath = os.path.join(baseIconFolder, iconName)
    resolvedPath = blue.paths.ResolvePath(iconPath)
    return (resolvedPath, os.path.exists(resolvedPath))


def _CleanupDuplicateRenderInfos(renderers):
    for i in range(0, len(renderers)):
        for j in range(i + 1, len(renderers)):
            for each in set(renderers[i].GetOutputPaths()).intersection(set(renderers[j].GetOutputPaths())):
                renderers[j].RemoveRenderInfo(each)

    empty = [ r for r in renderers if not r.HasRenderInfos() ]
    for r in empty:
        renderers.remove(r)


def _RunAutoDetectLanguageForRenderedIcon(loadMethod):
    languages = set()
    languages.add(Language.ENGLISH)
    for language in Language:
        if language not in [Language.ENGLISH, Language.AUTO_DETECT]:
            blue.motherLode.clear()
            prevLanguageID = blue.os.languageID
            blue.os.languageID = language
            import trinity
            trinity.WaitForResourceLoads()
            loadMethod()
            for name, resource in blue.motherLode.items():
                split = os.path.splitext(name)
                localizedPath = blue.paths.ResolvePath('%s.%s%s' % (split[0], language, split[1]))
                if os.path.exists(localizedPath):
                    languages.add(language)
                    break

            blue.os.languageID = prevLanguageID
            blue.motherLode.clear()

    return languages


def _RunAutoDetectLanguageForHanddrawnIcon(path):
    languages = set()
    languages.add(Language.ENGLISH)
    for language in Language:
        if language not in [Language.ENGLISH, Language.AUTO_DETECT]:
            name, ext = os.path.splitext(os.path.basename(path))
            localizedPath = os.path.join(os.path.dirname(path), '%s.%s%s' % (name, language, ext))
            if localizedPath != path and os.path.exists(blue.paths.ResolvePath(localizedPath)):
                languages.add(language)

    return languages


def _LoadForDna(dna, sofFactory):
    return sofFactory.BuildFromDNA(dna)


def _LoadForPath(path):
    blue.resMan.LoadObject(path)
