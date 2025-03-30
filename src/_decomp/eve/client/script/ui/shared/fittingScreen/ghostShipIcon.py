#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\ghostShipIcon.py
import carbonui.const as uiconst
import carbonui.fontconst
import evetypes
import inventorycommon
import log
import trinity
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.themeColored import LabelThemeColored
from eve.client.script.ui.services.menuSvcExtras import openFunctions
from eve.client.script.ui.shared.fitting.fittingUtil import GetTypeIDForController
from eve.client.script.ui.shared.fittingScreen.simulationModeTooltip import LoadSimulationIconTooltip
from eve.client.script.ui.shared.fittingScreen.tryFit import GhostFitShip
from eve.common.script.sys.eveCfg import GetActiveShip
from eve.common.script.sys.idCheckers import IsStructure
from localization import GetByLabel
from menu import MenuLabel
from menucheckers import SessionChecker, ItemChecker
from utillib import KeyVal
COLOR_BG = (0.0259, 0.0491, 0.075, 1.0)
OPACITY_NORMAL = 1.0
OPACITY_MOUSEOVER = 2.0
OPACITY_NORMAL_FRAME = 0.25
OPACITY_MOUSEOVER_FRAME = 0.45
OPACITY_NORMAL_ACTIVE_FRAME = 0.0
OPACITY_MOUSEOVER_ACTIVE_FRAME = 0.25

class GhostShipIcon(Container):
    default_name = 'GhostShipIcon'
    default_align = uiconst.TOPRIGHT
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.fittingSvc = sm.GetService('fittingSvc')
        self.enableButtonThread = None
        self.ConstructEnterSimulationCont()
        self.ConstructExitSimulationCont()
        self.iconSprite, self.iconTransform = AddIconAndIconTransform(self, self.width)
        self.bgActiveFrame = AddBackground(self)
        self.SetShipTypeID()

    def ConstructEnterSimulationCont(self):
        self.enterSimulationCont = Container(name='enterSimulationCont', parent=self)
        self.simulateLabel = LabelThemeColored(name='simulateLabel', fontStyle=carbonui.fontconst.STYLE_HEADER, parent=self.enterSimulationCont, fontsize=12, align=uiconst.CENTERBOTTOM, uppercase=True, text=GetByLabel('UI/Fitting/FittingWindow/Simulate'), opacity=0.75, top=-20)

    def ConstructExitSimulationCont(self):
        self.exitSimulationCont = Container(name='exitSimulationCont', parent=self)
        Fill(bgParent=self.exitSimulationCont, color=(0, 0, 0, 0.7))
        self.exitButtonIcon = ButtonIcon(parent=self.exitSimulationCont, texturePath='res:/UI/Texture/classes/Fitting/simExitOverlay.png', pos=(0, 0, 64, 64), align=uiconst.CENTER, iconSize=64, state=uiconst.UI_DISABLED)
        self.label = LabelThemeColored(fontStyle=carbonui.fontconst.STYLE_HEADER, parent=self.exitSimulationCont, fontsize=10, text='<center>%s' % GetByLabel('UI/Fitting/FittingWindow/ExitSimulation'), align=uiconst.CENTER, width=64, uppercase=True)

    def SetShipTypeID(self):
        if self.destroyed or not self.controller:
            return
        isSimulated = self.controller.IsSimulated()
        if isSimulated:
            self.typeID = GetTypeIDForController(session.shipid)
            self.iconSprite.blendMode = trinity.TR2_SBM_BLEND
            sm.GetService('photo').GetIconByType(self.iconSprite, self.typeID)
            self.exitSimulationCont.display = True
            self.enterSimulationCont.display = False
            self.ResetIcon()
        else:
            self.exitSimulationCont.display = False
            self.enterSimulationCont.display = True
            try:
                shipID = session.shipid
                self.typeID = GetTypeIDForController(shipID)
                self.iconSprite.blendMode = trinity.TR2_SBM_ADD
                texturePath = inventorycommon.typeHelpers.GetHoloIconPath(self.typeID)
            except AttributeError as e:
                texturePath = None
                log.LogException(e)
            finally:
                self.iconSprite.SetTexturePath(texturePath)

    def ResetIcon(self):
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, 1.0, duration=0.1, loops=1)
        self.iconTransform.StopAnimations()
        self.iconTransform.scale = (1.0, 1.0)

    def _GetSimulatedShipID(self):
        return sm.GetService('clientDogmaIM').GetFittingDogmaLocation().shipID

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_MOUSEOVER, duration=1.0, loops=1)
        uicore.animations.FadeTo(self.bgActiveFrame, self.bgActiveFrame.opacity, OPACITY_MOUSEOVER_ACTIVE_FRAME, duration=0.25, loops=1, curveType=uiconst.ANIM_OVERSHOT)
        if self.controller.IsSimulated():
            self.exitButtonIcon.OnMouseEnter()
            uicore.animations.MorphScalar(self.label, 'opacity', self.label.opacity, 1.5, duration=0.2)
        else:
            uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_MOUSEOVER, duration=1.0, loops=1)
            uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.3)
            uicore.animations.MorphScalar(self.simulateLabel, 'opacity', self.simulateLabel.opacity, 1.5, duration=0.2)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_NORMAL, duration=1.3)
        uicore.animations.FadeTo(self.bgActiveFrame, self.bgActiveFrame.opacity, OPACITY_NORMAL_ACTIVE_FRAME, duration=0.25, loops=1)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.0, 1.0), duration=0.3)
        self.exitButtonIcon.OnMouseExit()
        uicore.animations.MorphScalar(self.label, 'opacity', self.label.opacity, 0.75, duration=0.2)
        uicore.animations.MorphScalar(self.simulateLabel, 'opacity', self.simulateLabel.opacity, 0.75, duration=0.2)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadSimulationIconTooltip(tooltipPanel, self.controller.IsSimulated())

    def GetMenu(self, *args):
        m = []
        if self.controller.IsSimulated():
            m += [(MenuLabel('UI/Fitting/FittingWindow/SimulateMyShip', {'typeID': self.typeID}), sm.GetService('ghostFittingSvc').LoadCurrentShip, ())]
            m += [(MenuLabel('UI/Fitting/FittingWindow/ExitSimulationMode'), self.OnClick, ())]
        else:
            myActualShipTypeID = sm.GetService('clientDogmaIM').GetDogmaLocation().GetShip().typeID
            m += [(MenuLabel('UI/Fitting/FittingWindow/SimulateMyShip', {'typeID': myActualShipTypeID}), sm.GetService('ghostFittingSvc').LoadCurrentShip, ())]
            m += [(MenuLabel('UI/Fitting/FittingWindow/EnterSimulationMode'), self.OnClick, ())]
        return m

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.ToggleGhostFitting()

    def Close(self):
        self.controller = None
        Container.Close(self)

    def ToggleGhostFitting(self, *args):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        if self.enableButtonThread:
            self.enableButtonThread.kill()
            self.enableButtonThread = None
        self.state = uiconst.UI_DISABLED
        try:
            ghostFittingSvc.ToggleGhostFitting()
        finally:
            self.EnableButtonWithDelay()

    def EnableButtonWithDelay(self):
        if self.enableButtonThread:
            self.enableButtonThread.kill()
        self.enableButtonThread = uthread2.call_after_wallclocktime_delay(self.EnableButton, 0.5)

    def EnableButton(self):
        self.state = uiconst.UI_NORMAL
        self.enableButtonThread = None

    def GetDragData(self):
        fitting = KeyVal()
        fitting.shipTypeID, fitting.fitData, _ = self.GetFittingDictForOtherState()
        fitting.isCurrentShip = self.controller.IsSimulated() or self._GetSimulatedShipID() is None
        fitting.fittingID = None
        fitting.description = ''
        shipName = cfg.evelocations.Get(GetActiveShip()).locationName
        fitting.name = shipName
        entry = KeyVal()
        entry.fitting = fitting
        entry.label = fitting.name
        entry.displayText = fitting.name
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]

    def GetFittingDictForOtherState(self):
        fittingSvc = sm.GetService('fittingSvc')
        return fittingSvc.GetFittingDictForActiveShip()


class GhostShipIconSimple(Container):
    default_name = 'GhostShipIconSimple'
    default_align = uiconst.TOPRIGHT
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.itemID = attributes.itemID
        self.typeID = attributes.typeID
        self.invItem = attributes.invItem
        self.enableButtonThread = None
        self.iconSprite, self.iconTransform = AddIconAndIconTransform(self, self.width)
        self.iconSprite.blendMode = trinity.TR2_SBM_ADD
        self.bgActiveFrame = AddBackground(self)
        self.SetShipTypeID(self.typeID)

    def SetShipTypeID(self, typeID):
        texturePath = inventorycommon.typeHelpers.GetHoloIconPath(typeID)
        self.iconSprite.SetTexturePath(texturePath)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.SimulateShip()

    def SimulateShip(self, *args):
        if self.enableButtonThread:
            self.enableButtonThread.kill()
            self.enableButtonThread = None
        self.Disable()
        uicore.animations.MorphScalar(self, 'opacity', startVal=1.0, endVal=1.2, curveType=uiconst.ANIM_BOUNCE)
        try:
            if self.itemID == session.shipid:
                sm.GetService('ghostFittingSvc').LoadCurrentShipExternal()
            elif self.invItem:
                GhostFitShip(self.invItem)
            else:
                openFunctions.SimulateFitting(KeyVal(shipTypeID=self.typeID, fitData=[]))
        finally:
            self.EnableButtonWithDelay()

    def EnableButtonWithDelay(self):
        if self.enableButtonThread:
            self.enableButtonThread.kill()
        self.enableButtonThread = uthread2.call_after_wallclocktime_delay(self.EnableButton, 0.5)

    def EnableButton(self):
        self.Enable()
        self.enableButtonThread = None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        wrapWidth = 250
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 2)
        headerText = GetByLabel(GetSimulateLabelPath(self.itemID, self.typeID, self.invItem))
        bodyText = GetByLabel('Tooltips/FittingWindow/SimulateShipFittingDescription')
        tooltipPanel.AddLabelMedium(text=headerText, bold=True, colSpan=tooltipPanel.columns, wrapWidth=wrapWidth)
        tooltipPanel.AddLabelMedium(text=bodyText, colSpan=tooltipPanel.columns, wrapWidth=wrapWidth, color=(0.6, 0.6, 0.6, 1))

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_MOUSEOVER, duration=1.0, loops=1)
        uicore.animations.FadeTo(self.bgActiveFrame, self.bgActiveFrame.opacity, OPACITY_MOUSEOVER_ACTIVE_FRAME, duration=0.25, loops=1, curveType=uiconst.ANIM_OVERSHOT)
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_MOUSEOVER, duration=1.0, loops=1)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.3)

    def OnMouseExit(self, *args):
        self.AnimateMouseExit()

    def AnimateMouseExit(self):
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_NORMAL, duration=1.3)
        uicore.animations.FadeTo(self.bgActiveFrame, self.bgActiveFrame.opacity, OPACITY_NORMAL_ACTIVE_FRAME, duration=0.25, loops=1)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.0, 1.0), duration=0.3)

    def OnMouseDown(self, *args):
        self.top = 1

    def OnMouseUp(self, *args):
        self.top = 0


def AddIconAndIconTransform(parent, size):
    iconTransform = Transform(parent=parent, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
    iconSprite = Sprite(name='iconSprite', parent=iconTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, pos=(0,
     0,
     size,
     size), idx=0, opacity=OPACITY_NORMAL)
    return (iconSprite, iconTransform)


def AddBackground(parent):
    bgCont = Container(name='bgCont', parent=parent, padding=-4)
    bgActiveFrame = Frame(bgParent=bgCont, cornerSize=4, opacity=OPACITY_NORMAL_ACTIVE_FRAME, texturePath='res:/UI/Texture/classes/Fitting/simEdgeDecorationFrame.png')
    gridOverlay = Frame(bgParent=bgCont, cornerSize=10, opacity=0.5, texturePath='res:/UI/Texture/classes/Fitting/simBoxOverlay.png', padding=1)
    fill = Sprite(bgParent=bgCont, texturePath='res:/UI/Texture/classes/Fitting/simGridBack.png', opacity=0.75, padding=4)
    return bgActiveFrame


def GetSimulateLabelPath(itemID, typeID, invItem):
    if IsStructure(evetypes.GetCategoryID(typeID)):
        labelPath = 'UI/Fitting/FittingWindow/SimulateStructure'
    else:
        labelPath = 'UI/Fitting/FittingWindow/SimulateShip'
        if invItem:
            sessionChecker = SessionChecker(session, sm)
            item = ItemChecker(invItem, sessionChecker)
            if item.OfferSimulateShipFitting():
                labelPath = 'UI/Fitting/FittingWindow/SimulateShipFitting'
        elif itemID == session.shipid:
            labelPath = 'UI/Fitting/FittingWindow/SimulateShipFitting'
    return labelPath
