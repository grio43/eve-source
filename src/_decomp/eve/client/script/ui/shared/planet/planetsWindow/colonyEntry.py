#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetsWindow\colonyEntry.py
import eveicon
import trinity
from carbon.common.script.sys import service
from carbon.common.script.util.format import IntToRoman
from carbonui import uiconst, ButtonVariant, Density
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.cloneGrade import cloneStateUtil
from eve.client.script.ui.shared.cloneGrade.omegaRestrictedEntry import OmegaRestrictedEntry
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.shared.planet.pinContainers.storageIcon import StorageIcon
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtSystemSecStatus, FmtISKAndRound
from menu import MenuLabel
from inventorycommon import typeHelpers
from localization import GetByLabel
HEIGHT = 120
HEIGHT_COMPACT = 56
ICONSIZE = 32
ICONSIZE_COMPACT = 26
GENERIC_PADDING = 8

class BaseColonyEntry(Container):
    default_height = HEIGHT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isSelected = False
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, width=self.height, padding=(2, 2, 2, 3))
        self.ConstructCaptionCont()
        self.mainCont = Container(name='mainCont', parent=self, padLeft=GENERIC_PADDING, clipChildren=True)
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASE, opacity=0.05)
        self.underlay = ListEntryUnderlay(bgParent=self)

    def Update(self):
        pass

    def ConstructCaptionCont(self):
        self.captionCont = ContainerAutoSize(name='captionCont', parent=self, align=uiconst.TOTOP, padding=(0, 2, 0, 2), clipChildren=True)
        self.ConstructCaption()
        FillThemeColored(bgParent=self.captionCont, colorType=uiconst.COLORTYPE_UIHILIGHT)

    def ConstructCaption(self):
        self.caption = EveLabelLarge(parent=self.captionCont, align=uiconst.TOTOP, text=self.GetCaptionText(), padding=(GENERIC_PADDING,
         4,
         0,
         4), maxLines=1)

    def GetIconSize(self):
        return ICONSIZE

    def GetCaptionText(self):
        return ''

    def OnMouseEnter(self, *args):
        self.underlay.hovered = True

    def OnMouseExit(self, *args):
        self.underlay.hovered = False

    def SetSelected(self):
        self.isSelected = True
        self.underlay.Select()

    def SetDeselected(self):
        self.isSelected = False
        self.underlay.Deselect()

    def GetPlanetID(self):
        return None


class ColonyEntry(BaseColonyEntry):
    __notifyevents__ = ['OnPlanetSubmittingChanges']

    def ApplyAttributes(self, attributes):
        self.planetData = attributes.planetData
        self.onClickCallback = attributes.onClickCallback
        BaseColonyEntry.ApplyAttributes(self, attributes)
        self.ConstructRowContainers()
        self.ConstructNoActivityLabel(GetByLabel('UI/PI/Common/NoIndustrialActivity'))
        self.ReconstructItemConts()
        self.ConstructIcon()
        sm.RegisterNotify(self)

    def GetPlanetID(self):
        return self.planetData.planetID

    def ConstructRowContainers(self):
        self.topRowCont = ContainerAutoSize(name='topRowCont', parent=self.mainCont, align=uiconst.TOTOP, height=self.GetIconSize(), padTop=6, state=uiconst.UI_HIDDEN)
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self.mainCont, align=uiconst.BOTTOMRIGHT)
        self.bottomRowCont = ContainerAutoSize(name='bottomRowCont', parent=self.mainCont, align=uiconst.TOTOP, height=self.GetIconSize(), padTop=6, state=uiconst.UI_HIDDEN, clipChildren=True)

    def ConstructNoActivityLabel(self, text):
        self.noActivityLabel = EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, text=text, state=uiconst.UI_DISABLED, padTop=6, idx=0, showEllipsis=True)

    def ReconstructItemConts(self):
        self.topRowCont.Flush()
        self.buttonCont.Flush()
        self.CheckConstructExtractionCont()
        self.CheckConstructProductsCont()
        self.bottomRowCont.Flush()
        self.CheckConstructStorageCont()
        self.AddExtractionButton()
        if not self.topRowCont.children and not self.bottomRowCont.children:
            self.noActivityLabel.Show()
        else:
            self.noActivityLabel.Hide()

    def CheckConstructProductsCont(self):
        itemAmount = self.planetData.colony.colonyData.GetAllProcessorProducts()
        errorsTypeIDs = self.planetData.colony.colonyData.GetErrorsForProcessors()
        self._CheckConstructItemsCont(self.topRowCont, itemAmount, GetByLabel('UI/PI/Common/Production'), 'res:/UI/Texture/Planet/Icons/processor.png', errorTypeIDs=errorsTypeIDs)

    def CheckConstructExtractionCont(self):
        itemAmount = self.planetData.colony.colonyData.GetAllECUProducts()
        errorsTypeIDs = self.planetData.colony.colonyData.GetErrorsForECUPins()
        self._CheckConstructItemsCont(self.topRowCont, itemAmount, GetByLabel('UI/PI/Common/Extraction'), 'res:/UI/Texture/Planet/Icons/ecu.png', errorTypeIDs=errorsTypeIDs)

    def CheckConstructStorageCont(self):
        itemAmount = self.planetData.colony.colonyData.GetAllStoredProducts()
        errorsTypeIDs = self.planetData.colony.colonyData.GetErrorsForStorage()
        self._CheckConstructItemsCont(self.GetStorageContParent(), itemAmount, GetByLabel('UI/PI/Common/Storage'), 'res:/UI/Texture/Planet/Icons/storage.png', showAmount=True, errorTypeIDs=errorsTypeIDs)

    def GetStorageContParent(self):
        return self.bottomRowCont

    def _CheckConstructItemsCont(self, parent, itemAmount, hint, texturePath, showAmount = False, errorTypeIDs = None):
        if itemAmount:
            errorTypeIDs = errorTypeIDs or set()
            parent.state = uiconst.UI_PICKCHILDREN
            PlanetItemCont(parent=parent, align=uiconst.TOLEFT, itemAmount=itemAmount, height=self.GetIconSize(), texturePath=texturePath, hint=hint, padRight=38, onIconDblClickCallback=self.OnDblClick, onMouseEnterCallback=self.OnMouseEnter, showAmount=showAmount, errorTypeIDs=errorTypeIDs)

    def ConstructIcon(self):
        self.ConstructNeedsAttentionIcon()
        if self.planetData:
            self.icon = eveIcon.Icon(parent=self.iconCont, align=uiconst.TOALL, typeID=self.planetData.planetTypeID, itemID=self.planetData.planetID, effectOpacity=0.0)
            self.CheckUpdateNeedsAttentionIndication()

    def AddExtractionButton(self):
        planetSvc = sm.GetService('planetSvc')
        colonyData = self.planetData.colony.colonyData
        if planetSvc.IsSubmittingInProgressForPlanet(self.GetPlanetID()) and colonyData.GetECUPins():
            self._AddExtractionButton(disabledReasonPath='UI/PI/Common/PlanetBusyUpdating')
            return
        if self.planetData.IsEditingPlanet():
            return
        if not colonyData.CanEcuPinsBeRestarted():
            return
        disabledReasonPath = None
        if planetSvc.IsSubmittingInProgressOrThrottled():
            disabledReasonPath = 'UI/PI/Common/PlanetBusyUpdating'
        self._AddExtractionButton(disabledReasonPath)

    def _AddExtractionButton(self, disabledReasonPath = None):
        if self.topRowCont.children and self.bottomRowCont.children:
            self.buttonCont.SetAlign(uiconst.TORIGHT)
        else:
            self.buttonCont.SetAlign(uiconst.BOTTOMRIGHT)
        enabled = disabledReasonPath is None
        hint = GetByLabel(disabledReasonPath) if disabledReasonPath else ''
        Button(name='restartExtraction', parent=self.buttonCont, label=GetByLabel('UI/PI/Common/RestartExtaction'), func=self.RestartExtractors, align=uiconst.BOTTOMRIGHT, texturePath=eveicon.refresh, pos=(GENERIC_PADDING,
         2,
         0,
         0), variant=ButtonVariant.GHOST, enabled=enabled, hint=hint)

    def CheckUpdateNeedsAttentionIndication(self):
        if self.IsAttentionNeeded():
            self.icon.spriteEffect = trinity.TR2_SFX_COLOROVERLAY
            self.icon.saturation = 0.25
            self.needsAttentionCont.Show()
        else:
            self.icon.spriteEffect = trinity.TR2_SFX_COPY
            self.icon.saturation = 1.0
            self.needsAttentionCont.Hide()

    def ConstructNeedsAttentionIcon(self):
        self.needsAttentionCont = Container(name='needsAttentionCont', parent=self.iconCont)
        Sprite(name='needsAttentionCircle', parent=self.needsAttentionCont, texturePath='res:/UI/Texture/Planet/planetsWnd/circleBg.png', align=uiconst.CENTER, pos=(0, 0, 98, 98))
        self.needsAttentionCircle = Sprite(name='needsAttentionCircle', parent=self.needsAttentionCont, texturePath='res:/UI/Texture/Planet/planetsWnd/needsAttentionIcon.png', align=uiconst.CENTER, pos=(0, 0, 31, 31), color=Color.RED)
        animations.FadeTo(self.needsAttentionCircle, 0.2, 1.0, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def IsAttentionNeeded(self):
        return self.planetData.colony.colonyData.IsSomePinNeedingAttention()

    def GetCaptionText(self):
        securityText = self.GetSecurityStatusTxt(self.planetData.solarSystemID)
        planetName = cfg.evelocations.Get(self.planetData.planetID).locationName
        planetTypeName = GetByLabel(planetConst.PLANETTYPE_NAMES[self.planetData.planetTypeID])
        numInstallations = len(self.planetData.colony.colonyData.pins)
        numInstallationsTxt = GetByLabel('UI/PI/Common/NumInstallations', numInstallations=numInstallations)
        captionText = '%s %s - %s - %s' % (securityText,
         planetName,
         planetTypeName,
         numInstallationsTxt)
        return captionText

    def GetSecurityStatusTxt(self, solarSystemID):
        securityStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
        sec, col = FmtSystemSecStatus(securityStatus, 1)
        color = Color.RGBtoHex(*col)
        text = '<color=%s>%s</color>' % (color, sec)
        return text

    def GetMenu(self, *args):
        if not self.planetData:
            return
        menu = []
        menuSvc = sm.GetService('menu')
        solarSystemID = self.planetData.solarSystemID
        planetID = self.planetData.planetID
        if solarSystemID != session.solarsystemid:
            mapItem = sm.StartService('map').GetItem(solarSystemID)
            if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                gmExtrasLabel = MenuLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/GMWMExtrasCommand')
                menu += [(gmExtrasLabel, ('isDynamic', menuSvc.GetGMMenu, (planetID,
                    None,
                    None,
                    None,
                    mapItem)))]
            menu += menuSvc.MapMenu(solarSystemID)
            isOpen = sm.GetService('viewState').IsViewActive('planet') and sm.GetService('planetUI').planetID == planetID
            if isOpen:
                menu += [[MenuLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ()]]
            else:
                menu += [(MenuLabel('UI/PI/Common/ViewInPlanetMode'), sm.GetService('planetUI').Open, (planetID,))]
            typeID = self.planetData.planetTypeID
            menu += [(MenuLabel('UI/Commands/ShowInfo'), menuSvc.ShowInfo, (typeID,
               planetID,
               0,
               None,
               None))]
        else:
            menu += menuSvc.CelestialMenu(planetID)
        return menu

    def OnClick(self, *args):
        self.onClickCallback(self)

    def OnDblClick(self, *args):
        sm.GetService('planetUI').Open(self.planetData.planetID)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.IsAttentionNeeded():
            tooltipPanel.LoadGeneric1ColumnTemplate()
            text = '<color=red>%s</color>' % GetByLabel('UI/PI/Common/ColonyRequiresAttention')
            tooltipPanel.AddLabelMedium(text=text)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def RestartExtractors(self, btn, *args):
        btn.Disable()
        restarted = self.planetData.RestartExtractors()
        if restarted:
            ShowQuickMessage(GetByLabel('UI/PI/Common/RestartExtractionSuccess'))
        else:
            ShowQuickMessage(GetByLabel('UI/PI/Common/RestartExtractionFailure'))

    def OnPlanetSubmittingChanges(self):
        self.Update()

    def Update(self):
        self.CheckUpdateNeedsAttentionIndication()
        self.ReconstructItemConts()


class ColonyEntryCompact(ColonyEntry):
    default_height = HEIGHT_COMPACT

    def ConstructNeedsAttentionIcon(self):
        self.needsAttentionCont = Container(name='needsAttentionCont', parent=self.iconCont)
        self.needsAttentionCircle = Sprite(name='needsAttentionCircle', parent=self.needsAttentionCont, texturePath='res:/UI/Texture/Planet/planetsWnd/needsAttentionIcon.png', align=uiconst.CENTER, pos=(0, 0, 31, 31), color=Color.RED)
        animations.FadeTo(self.needsAttentionCircle, 0.2, 1.0, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def ConstructRowContainers(self):
        self.buttonCont = ContainerAutoSize(name='buttonCont', parent=self.mainCont, align=uiconst.TORIGHT)
        self.topRowCont = ContainerAutoSize(name='topRowCont', parent=self.mainCont, align=uiconst.TOTOP, height=self.GetIconSize(), padTop=0, state=uiconst.UI_HIDDEN, clipChildren=True)
        self.bottomRowCont = ContainerAutoSize(name='bottomRowCont', parent=self.mainCont, align=uiconst.TOTOP, height=self.GetIconSize(), padTop=6, state=uiconst.UI_HIDDEN)

    def GetStorageContParent(self):
        return self.topRowCont

    def GetIconSize(self):
        return ICONSIZE_COMPACT

    def ConstructCaption(self):
        self.caption = EveLabelMedium(parent=self.captionCont, align=uiconst.CENTERLEFT, text=self.GetCaptionText(), padding=(GENERIC_PADDING,
         1,
         0,
         3))

    def _AddExtractionButton(self, disabledReasonPath = True):
        enabled = disabledReasonPath is None
        hint = GetByLabel(disabledReasonPath) if disabledReasonPath else GetByLabel('UI/PI/Common/RestartExtaction')
        Button(name='restartExtraction', parent=self.buttonCont, func=self.RestartExtractors, align=uiconst.CENTERRIGHT, texturePath=eveicon.refresh, density=Density.COMPACT, hint=hint, pos=(GENERIC_PADDING,
         2,
         0,
         0), variant=ButtonVariant.GHOST, enabled=enabled)


class ColonyEntryEmpty(BaseColonyEntry):

    def ApplyAttributes(self, attributes):
        BaseColonyEntry.ApplyAttributes(self, attributes)
        self.slotIndex = attributes.slotIndex
        self.slotsTotal = attributes.slotsTotal
        if self.IsLocked() or not cloneStateUtil.IsOmega():
            self.ConstructIconLocked()
        else:
            self.ConstructIconAvailable()
        if not self.IsLocked() and not cloneStateUtil.IsOmega():
            self.ConstructIconOmegaNeeded()
        else:
            self.ConstructLabel()

    def ConstructLabel(self):
        EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, text=self.GetMainText(), state=uiconst.UI_NORMAL, padTop=6, idx=0, maxLines=5)

    def ConstructIconOmegaNeeded(self):
        OmegaRestrictedEntry(parent=self.mainCont, align=uiconst.TOTOP, height=30, padTop=8, text=GetByLabel('UI/CloneState/PlanetaryProductionDisabled'), hint=GetByLabel('UI/CloneState/PlanetExportingDisabledHint'))

    def ConstructIconAvailable(self):
        iconSize = self.GetAvailableIconSize()
        Sprite(parent=self.iconCont, align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/Planet/PlanetsWnd/slotUnlocked.png')

    def GetAvailableIconSize(self):
        return 98

    def ConstructIconLocked(self):
        iconSize = self.GetLockedIconSize()
        Sprite(parent=self.iconCont, align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/Planet/PlanetsWnd/slotLocked.png')
        SpriteThemeColored(name='hatchesBg', bgParent=self.iconCont, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', tileX=True, tileY=True, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.3)

    def GetLockedIconSize(self):
        return 68

    def GetMainText(self):
        if self.IsLocked():
            return self._GetLockedText()
        else:
            typeID = appConst.typeBarrenCommandCenter
            marketGroup, _ = sm.GetService('marketutils').FindMarketGroup(typeID)
            return GetByLabel('UI/PI/Common/RequiresCommandCenter', marketGroupID=marketGroup.marketGroupID)

    def _GetLockedText(self):
        return GetByLabel('UI/PI/Common/RequiresSkillLevelX', typeID=appConst.typeInterplanetaryConsolidation, skillLevel=IntToRoman(self.slotIndex))

    def IsLocked(self):
        return self.slotIndex >= self.slotsTotal

    def GetCaptionText(self):
        return GetByLabel('UI/PI/Common/UnestablishedColony')


class ColonyEntryEmptyCompact(ColonyEntryEmpty):
    default_height = HEIGHT_COMPACT

    def GetAvailableIconSize(self):
        return 49

    def GetLockedIconSize(self):
        return 34

    def GetIconSize(self):
        return ICONSIZE_COMPACT

    def ConstructLabel(self):
        EveLabelMedium(parent=self.mainCont, align=uiconst.TOTOP, text=self.GetMainText(), state=uiconst.UI_NORMAL, idx=0, maxLines=2)

    def ConstructCaption(self):
        self.caption = EveLabelMedium(parent=self.captionCont, align=uiconst.CENTERLEFT, text=self.GetCaptionText(), padding=(GENERIC_PADDING,
         1,
         0,
         3))


class PlanetItemCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.hint = attributes.hint
        self.itemAmount = attributes.itemAmount
        texturePath = attributes.texturePath
        self.showAmount = attributes.Get('showAmount', False)
        self.errorTypeIDs = attributes.Get('errorTypeIDs', set())
        self.onIconDblClickCallback = attributes.onIconDblClickCallback
        self.onMouseEnterCallback = attributes.onMouseEnterCallback
        groupIconCont = Container(name='groupIconCont', parent=self, align=uiconst.TOLEFT, width=self.height)
        iconSize = self.height - 8
        icon = SpriteThemeColored(name='groupIcon', parent=groupIconCont, texturePath=texturePath, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), opacity=0.9)
        icon.OnDblClick = self.onIconDblClickCallback
        icon.OnMouseEnter = self.onMouseEnterCallback
        icon.LoadTooltipPanel = self.LoadIconTooltipPanel
        if None in self.errorTypeIDs:
            self.AddWarningLine(groupIconCont, padRight=8)
        for typeID, amount in self.itemAmount.iteritems():
            if not self.showAmount:
                amount = None
            storageIconCont = Container(parent=self, align=uiconst.TOLEFT, width=self.height, padRight=4)
            if typeID in self.errorTypeIDs:
                self.AddWarningLine(storageIconCont)
            icon = StorageIcon(parent=storageIconCont, align=uiconst.CENTER, pos=(0,
             0,
             self.height,
             self.height), typeID=typeID, amount=amount)
            icon.OnDblClick = self.onIconDblClickCallback
            icon.OnMouseEnter = self.onMouseEnterCallback

        self.SetSizeAutomatically()

    def AddWarningLine(self, parent, padRight = 0):
        cont = Container(parent=parent, align=uiconst.TOBOTTOM_NOPUSH, height=10, padRight=padRight, state=uiconst.UI_NORMAL)
        Line(parent=cont, align=uiconst.TOBOTTOM_NOPUSH, outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW, color=eveColor.CHERRY_RED)
        cont.hint = GetByLabel('UI/PI/Common/ColonyRequiresAttention')

    def LoadIconTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.hint)
        if self.showAmount:
            totalPriceText = self.GetTotalPriceText()
            tooltipPanel.AddLabelMedium(text=totalPriceText)

    def GetTotalPriceText(self):
        total = 0
        for typeID, amount in self.itemAmount.iteritems():
            price = typeHelpers.GetAveragePrice(typeID)
            if price:
                total += price * amount

        return GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(total, False))
