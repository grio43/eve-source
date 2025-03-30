#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\factory\recipe.py
import evetypes
import os
from itertoolsext.Enum import Enum
from evegraphics.utils import BuildSOFDNAFromGraphicID
from fsdBuiltData.common.iconIDs import GetIcon
from fsdBuiltData.common.graphicIDs import GetGraphic
from platformtools.compatibility.exposure.dnahelper import DNAParts
import inventorycommon.const as invconst
import eve.common.lib.appConst as appconst
import iconrendering2.const
from iconrendering2.const import IconStyle, IconBackground, IconOverlay
from iconrendering2.const import RENDER_64, RENDER_128, RENDER_64_128_512, OUTLINE_COLOR
from iconrendering2.const import GetIconFaction, GetBackgroundPathAndTransparency

@Enum

class IconType(object):
    SUN = 'SUN'
    PLANETARY_PIN = 'PLANETARY_PIN'
    SOF_SHIP_OR_STRUCTURE = 'SOF_SHIP_OR_STRUCTURE'
    SOF_OTHER = 'SOF_OTHER'
    HANDDRAWN = 'HANDDRAWN'
    OTHER = 'OTHER'
    NONE = 'NONE'


class IconTypeRenderData(object):

    def __init__(self, renderSizesAndFormats, useMetagroup, useMetadata, writeSize):
        self.renderSizesAndFormats = renderSizesAndFormats
        self.useMetagroup = useMetagroup
        self.writeSize = writeSize
        self.useMetadata = useMetadata


_ICON_TYPES_RENDER_DATA = {}
_ICON_TYPES_RENDER_DATA[IconType.SUN] = {}
_ICON_TYPES_RENDER_DATA[IconType.SUN][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64_128_512, False, True, True)
_ICON_TYPES_RENDER_DATA[IconType.PLANETARY_PIN] = {}
_ICON_TYPES_RENDER_DATA[IconType.PLANETARY_PIN][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64_128_512, False, False, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER] = {}
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64_128_512, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.BP_ORIGINAL] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.BP_COPY] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.BP_REACTION] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.BP_RELIC] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_OTHER][IconStyle.BP_DUST] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE] = {}
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64_128_512, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.BP_ORIGINAL] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.BP_COPY] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.BP_REACTION] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.BP_RELIC] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.BP_DUST] = IconTypeRenderData(RENDER_64, True, True, True)
_ICON_TYPES_RENDER_DATA[IconType.SOF_SHIP_OR_STRUCTURE][IconStyle.HOLOGRAM] = IconTypeRenderData(RENDER_128, False, True, False)
_ICON_TYPES_RENDER_DATA[IconType.OTHER] = {}
_ICON_TYPES_RENDER_DATA[IconType.OTHER][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64_128_512, False, False, True)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN] = {}
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.STANDARD] = IconTypeRenderData(RENDER_64, True, False, False)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.BP_ORIGINAL] = IconTypeRenderData(RENDER_64, True, False, False)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.BP_COPY] = IconTypeRenderData(RENDER_64, True, False, False)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.BP_REACTION] = IconTypeRenderData(RENDER_64, True, False, False)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.BP_RELIC] = IconTypeRenderData(RENDER_64, True, False, False)
_ICON_TYPES_RENDER_DATA[IconType.HANDDRAWN][IconStyle.BP_DUST] = IconTypeRenderData(RENDER_64, True, False, False)

class IconRecipe(object):

    def __init__(self, input, sizesAndFormats, background, overlay, useMetagroup, useMetadata, outline, writeSize, faction):
        self.input = input
        self.sizesAndFormats = sizesAndFormats
        self.background, self.backgroundTransparency = GetBackgroundPathAndTransparency(background, faction)
        self.overlay = overlay
        self.useMetagroup = useMetagroup
        self.useMetadata = useMetadata
        self.outline = outline
        self.writeSize = writeSize


class RenderedIconRecipe(IconRecipe):

    def __init__(self, input, sizesAndFormats, background, overlay, useMetagroup, useMetadata, outline, writeSize, faction, useExistingIcons, sourceFolder):
        super(RenderedIconRecipe, self).__init__(input, sizesAndFormats, background, overlay, useMetagroup, useMetadata, outline, writeSize, faction)
        self.useExistingIcons = useExistingIcons
        self.sourceFolder = sourceFolder


class HanddrawnIconRecipe(IconRecipe):

    def __init__(self, input, sizesAndFormats, background, overlay, useMetagroup, useMetadata, outline, writeSize, faction):
        super(HanddrawnIconRecipe, self).__init__(input, sizesAndFormats, background, overlay, useMetagroup, useMetadata, outline, writeSize, faction)
        self.sourceIcons = {}

    def AddSourceIcon(self, path, size):
        self.sourceIcons[size] = path


class TypeData(object):

    def __init__(self, typeID, resourceMapper):
        self.typeID = typeID
        self.iconType = IconType.NONE
        self.groupID = evetypes.GetGroupID(typeID)
        self.categoryID = evetypes.GetCategoryID(typeID)
        self.graphicID = evetypes.GetGraphicID(typeID)
        self.iconID = evetypes.GetIconID(typeID)
        self.metagroupID = evetypes.GetMetaGroupID(typeID)
        self.isRenderable = self.graphicID and evetypes.IsRenderable(self.typeID)
        self.graphicFile = None
        self.graphicIconFolder = None
        self.dna = None
        self.dnaParts = None
        if self.graphicID:
            self.graphicFile = resourceMapper.GetGraphicFileForGraphicID(self.graphicID)
            graphicIDObject = GetGraphic(self.graphicID)
            if graphicIDObject and graphicIDObject.iconInfo and graphicIDObject.iconInfo.folder:
                self.graphicIconFolder = graphicIDObject.iconInfo.folder
            if self.isRenderable and all(resourceMapper.GetSOFDataForGraphicID(self.graphicID)):
                self.dna = BuildSOFDNAFromGraphicID(self.graphicID)
                self.dnaParts = DNAParts(self.dna)
        self.iconFile = None
        if self.iconID:
            iconIDObject = GetIcon(self.iconID)
            if iconIDObject:
                self.iconFile = iconIDObject.iconFile
        self.isSof = self.isRenderable and self.dna
        if self.isRenderable:
            if self.groupID == appconst.groupSun:
                self.iconType = IconType.SUN
            elif self.categoryID == appconst.categoryPlanetaryInteraction:
                self.iconType = IconType.PLANETARY_PIN
            elif self.categoryID in [appconst.categoryShip, appconst.categoryStructure]:
                self.iconType = IconType.SOF_SHIP_OR_STRUCTURE
            elif self.isSof:
                self.iconType = IconType.SOF_OTHER
            elif self.graphicFile:
                self.iconType = IconType.OTHER
        elif self.iconID and self.iconFile:
            self.iconType = IconType.HANDDRAWN
        self.isBlueprintOriginalOrCopy = self.categoryID == invconst.categoryBlueprint
        self.isBlueprintRelic = self.categoryID == invconst.categoryAncientRelic
        self.isBlueprintReaction = self.categoryID == invconst.categoryReaction
        self.isBlueprintDust = self.categoryID == invconst.categoryInfantry

    def GetRecipes(self, onlyUseExistingBaseIcons, renderMetagroupOverlay):
        recipes = {}
        availableStyles = self.GetIconStyles()
        for style, data in _ICON_TYPES_RENDER_DATA.get(self.iconType, {}).iteritems():
            if style & availableStyles:
                background, overlay = self._GetBackgroundAndOverlay(style)
                faction = GetIconFaction(self.dnaParts.hull, self.dnaParts.faction, self.dnaParts.race) if self.isSof else None
                outline = self._GetOutline(style)
                useMetagroup = data.useMetagroup if renderMetagroupOverlay else False
                recipe = None
                if self.iconType == IconType.HANDDRAWN:
                    recipe = HanddrawnIconRecipe(self._GetInput(style), data.renderSizesAndFormats, background, overlay, useMetagroup, data.useMetadata, outline, data.writeSize, faction)
                    recipe.AddSourceIcon(self.iconFile, 64)
                elif self.iconType in [IconType.SUN,
                 IconType.PLANETARY_PIN,
                 IconType.SOF_SHIP_OR_STRUCTURE,
                 IconType.SOF_OTHER]:
                    recipe = RenderedIconRecipe(self._GetInput(style), data.renderSizesAndFormats, background, overlay, useMetagroup, data.useMetadata, outline, data.writeSize, faction, onlyUseExistingBaseIcons, self.graphicIconFolder)
                elif self.iconType == IconType.OTHER and onlyUseExistingBaseIcons:
                    recipe = RenderedIconRecipe(self._GetInput(style), data.renderSizesAndFormats, background, overlay, useMetagroup, data.useMetadata, outline, data.writeSize, faction, onlyUseExistingBaseIcons, self.graphicIconFolder)
                if recipe:
                    recipes[style] = recipe

        return recipes

    def _GetInput(self, style):
        if self.iconType == IconType.HANDDRAWN:
            return os.path.splitext(os.path.basename(self.iconFile))[0]
        elif self.dna and style == IconStyle.HOLOGRAM:
            return self.dnaParts.hull
        else:
            return self.graphicID

    def _GetBackgroundAndOverlay(self, style):
        if self.iconType == IconType.HANDDRAWN and style == IconStyle.STANDARD:
            return (IconBackground.TRANSPARENT, IconOverlay.NONE)
        elif self.iconType in [IconType.SOF_SHIP_OR_STRUCTURE, IconType.SOF_OTHER] and style == IconStyle.STANDARD:
            background = IconBackground.RACIAL if iconrendering2.const.USE_STATIC_BACKGROUNDS else IconBackground.NONE
            return (background, IconOverlay.NONE)
        elif style in [IconStyle.STANDARD, IconStyle.HOLOGRAM]:
            return (IconBackground.NONE, IconOverlay.NONE)
        elif style == IconStyle.TRANSPARENT:
            return (IconBackground.TRANSPARENT, IconOverlay.NONE)
        else:
            return GetBlueprintBackgroundAndOverlay(style)

    def _GetOutline(self, style):
        outline = None
        if self.isSof and style in [IconStyle.STANDARD, IconStyle.TRANSPARENT]:
            iconFaction = GetIconFaction(self.dnaParts.hull, self.dnaParts.faction, self.dnaParts.race)
            outline = OUTLINE_COLOR.get(iconFaction, None) if iconrendering2.const.OUTLINE_THICKNESS > 0 else None
        return outline

    def GetIconStyles(self):
        if self.isBlueprintOriginalOrCopy:
            return IconStyle.BP_ORIGINAL | IconStyle.BP_COPY
        elif self.isBlueprintRelic:
            return IconStyle.BP_RELIC
        elif self.isBlueprintReaction:
            return IconStyle.BP_REACTION
        elif self.isBlueprintDust:
            return IconStyle.BP_DUST
        elif self.iconType == IconType.SOF_SHIP_OR_STRUCTURE:
            return IconStyle.STANDARD | IconStyle.TRANSPARENT | IconStyle.HOLOGRAM
        else:
            return IconStyle.STANDARD


def GetBlueprintBackgroundAndOverlay(style):
    if style == IconStyle.BP_ORIGINAL:
        return (IconBackground.BP_ORIGINAL, IconOverlay.BP_ORIGINAL)
    elif style == IconStyle.BP_COPY:
        return (IconBackground.BP_COPY, IconOverlay.BP_COPY)
    elif style == IconStyle.BP_REACTION:
        return (IconBackground.BP_REACTION, IconOverlay.BP_REACTION)
    elif style == IconStyle.BP_RELIC:
        return (IconBackground.BP_RELIC, IconOverlay.BP_RELIC)
    elif style == IconStyle.BP_DUST:
        return (IconBackground.BP_DUST, IconOverlay.NONE)
    else:
        return (IconBackground.NONE, IconOverlay.NONE)
