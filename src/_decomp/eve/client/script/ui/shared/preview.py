#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\preview.py
import uthread2
from brennivin.itertoolsext import first, first_or_default
from carbon.common.script.util.format import FmtDist
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from characterdata.races import get_race_name
from cosmetics.client.shipSkinLicensesSvc import get_ship_skin_license_svc
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.paperDoll.paperDollImpl import Doll, Factory
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollCharacter
from eve.client.script.ui.camera.cameraUtil import GetModelLookAtOffset
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveHeaderSmall, Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.window import Window
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation, SceneContainer
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.login.charcreation.ccUtil import GenderIDToPaperDollGender
from eve.client.script.ui.shared.skins.controller import SkinPanelController, ThirdPartySkinWrapper, GetSkinnedShipModel
from eve.client.script.ui.shared.skins.skinPanel import SkinPanel
from eve.client.script.ui.station.assembleModularShip import AssembleShip
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from eve.common.script.paperDoll.paperDollDefinitions import ACCESSORIES_CATEGORIES, BODY_CATEGORIES, DOLL_PARTS, GENDER, HEAD_CATEGORIES, LOD_SKIN
from eve.common.script.sys.eveCfg import IsPreviewable
from eve.common.script.sys.idCheckers import IsShipType
import evetypes
from eveexceptions import UserError
from fsdBuiltData.common.graphicIDs import GetGraphicFile, GetSofFactionName
from inventorycommon.util import IsModularShip
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException
from utillib import KeyVal
import mathext
import carbon.common.script.sys.service as service
import carbonui.const as uiconst
import charactercreator.const as ccConst
import eve.common.lib.appConst as appConst
import evegraphics.settings as gfxsettings
import evegraphics.utils as gfxutils
import eveSpaceObject
import eveSpaceObject.spaceobjanimation as soanimation
import geo2
import inventorycommon.const as invconst
import localization
import log
import math
import re
import sys
import trinity
import uthread
import inventorycommon.typeHelpers
import charactercreator.client.animparams as animparams
from eve.client.script.environment.sofService import GetSofService
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
MESH_NAMES_BY_GROUPID = {invconst.groupApparelEyewear: [ACCESSORIES_CATEGORIES.ACCESSORIES],
 invconst.groupApparelProsthetics: [ACCESSORIES_CATEGORIES.SLEEVESLOWER],
 invconst.groupApparelTattoos: [ACCESSORIES_CATEGORIES.SLEEVESLOWER],
 invconst.groupApparelPiercings: [],
 invconst.groupApparelScars: [BODY_CATEGORIES.SCARS],
 invconst.groupApparelMidLayer: [BODY_CATEGORIES.TOPINNER],
 invconst.groupApparelOuter: [BODY_CATEGORIES.OUTER],
 invconst.groupApparelTops: [BODY_CATEGORIES.TOPINNER],
 invconst.groupApparelBottoms: [BODY_CATEGORIES.BOTTOMOUTER],
 invconst.groupApparelFootwear: [BODY_CATEGORIES.FEET],
 invconst.groupApparelHairStyles: [DOLL_PARTS.HAIR, DOLL_PARTS.HEAD],
 invconst.groupApparelMakeup: [HEAD_CATEGORIES.MAKEUP],
 invconst.groupApparelAugmentations: [DOLL_PARTS.HEAD],
 invconst.groupApparelMasks: [ACCESSORIES_CATEGORIES.ACCESSORIES]}
MANNEQUIN_RES_BY_GENDER = {GENDER.MALE: 'res:/Graphics/Character/DNAFiles/Mannequin/MaleMannequin.prs',
 GENDER.FEMALE: 'res:/Graphics/Character/DNAFiles/Mannequin/FemaleMannequin.prs'}
PAPERDOLL_CATEGORIES_COVERING = {ccConst.bottommiddle: [ccConst.bottomouter]}

def GetPaperDollResource(typeID, gender = None):
    assets = filter(lambda a: a.typeID == typeID, cfg.paperdollResources)
    if len(assets) == 0:
        log.LogWarn('PreviewWnd::PreviewType - No asset matched the typeID {}'.format(typeID))
        return None
    default_asset = first(assets)
    unisex_asset = first_or_default(assets, lambda a: a.resGender is None, default_asset)
    return first_or_default(assets, lambda a: a.resGender == gender, unisex_asset)


def SetupAnimations(model):
    if not model.controllers:
        model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
    soanimation.TriggerDefaultStates(model)


class Preview(service.Service):
    __guid__ = 'svc.preview'
    __servicename__ = 'preview'
    __displayname__ = 'Preview Service'
    __exportedcalls__ = {'PreviewType': [],
     'PreviewCharacter': [],
     'DisplayCharacter': []}
    __dependencies__ = []

    def Run(self, memStream = None):
        service.Service.Run(self, memStream=memStream)
        self.state = service.SERVICE_RUNNING

    def PreviewType(self, typeID, subsystems = None, itemID = None, animate = True, otherTypeID = None, skin_state = None, **kwargs):
        categoryID = evetypes.GetCategoryID(typeID)
        shipTypeID = None
        skin = None
        if categoryID == invconst.categoryShip:
            shipTypeID = typeID
        elif categoryID == invconst.categoryShipSkin:
            skin = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(typeID)
            shipTypeID = otherTypeID if otherTypeID and otherTypeID in skin.types else skin.types[0]
        if shipTypeID:
            params = {'skin': skin}
            from eve.client.script.ui.shared.info.shipInfoConst import TAB_SKINS
            sm.GetService('info').ShowInfo(typeID=shipTypeID, itemID=itemID, selectTabType=TAB_SKINS, params=params)
            return
        wnd = PreviewWnd.Open(typeID=typeID)
        if wnd:
            wnd.PreviewType(typeID=typeID, subsystems=subsystems, itemID=itemID, animate=animate, otherTypeID=otherTypeID, skin_state=skin_state, **kwargs)
        return wnd

    def PreviewCharacter(self, charID):
        if charID in appConst.auraAgentIDs:
            return
        dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        wnd = PreviewCharacterWnd.GetIfOpen()
        if wnd:
            wnd.PreviewCharacter(charID=charID, dna=dna)
        else:
            wnd = PreviewCharacterWnd.Open(charID=charID, dna=dna)
        return wnd

    def DisplayCharacter(self, charID):
        dna = sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        wnd = PreviewCharacterWnd.GetIfOpen()
        if wnd:
            wnd.PreviewCharacter(charID=charID, dna=dna)
        else:
            PreviewCharacterWnd.Open(charID=charID, dna=dna)


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.5, opacityMouseDown=1.0, bgElementFunc=lambda parent, _: parent.hilite, audioOnEntry=uiconst.SOUND_ENTRY_HOVER, audioOnClick=uiconst.SOUND_ENTRY_SELECT))

class SidePanelButton(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(SidePanelButton, self).ApplyAttributes(attributes)
        self.onClick = attributes.onClick
        self.expanded = attributes.get('expanded', False)
        Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/preview/tab.png', width=20, height=80)
        self.hilite = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/preview/tab-hilite.png', width=20, height=80, opacity=0.0)
        rotation = 0 if self.expanded else math.pi
        self.tabIcon = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=2, top=32, texturePath='res:/UI/Texture/classes/preview/tab-icon.png', width=16, height=16, rotation=rotation)

    def OnClick(self, *args):
        self.expanded = not self.expanded
        self.AnimClick()
        self.onClick()

    def AnimClick(self):
        rotation = 0 if self.expanded else math.pi
        uicore.animations.MorphScalar(self.tabIcon, 'rotation', startVal=self.tabIcon.rotation, endVal=rotation, duration=0.3)


class PreviewWnd(Window):
    __guid__ = 'form.PreviewWnd'
    default_windowID = 'previewWnd'
    default_minSize = (420, 330)
    default_caption = localization.GetByLabel('UI/Preview/PreviewCaption')
    PANEL_WIDTH = 416

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        width = self.PANEL_WIDTH if self.IsPanelExpanded() else 0
        self.sidePanelWrapper = Container(name='sidePanelWrapper', parent=self.sr.main, align=uiconst.TOLEFT, width=width, bgColor=(1.0, 1.0, 1.0, 0.05), padLeft=-16, padBottom=-16, clipChildren=True)
        self.sidePanel = Container(name='SidePanel', parent=self.sidePanelWrapper, align=uiconst.TOLEFT, width=self.PANEL_WIDTH, padding=8)
        self.skinController = SkinPanelController(hullTypeID=None)
        self.skinPanel = SkinPanel(parent=self.sidePanel, align=uiconst.TOLEFT, width=self.PANEL_WIDTH - 16, controller=self.skinController, settingsPrefix='Preview_SkinPanel', logContext='PreviewWindow')
        mainCont = Container(name='MainContainer', parent=self.sr.main, align=uiconst.TOALL, padding=(16, 0, -16, -16))
        opacity = 1.0 if self.IsPanelEnabled() else 0.0
        self.sidePanelButton = SidePanelButton(parent=mainCont, align=uiconst.CENTERLEFT, opacity=opacity, onClick=self.ToggleSidePanel, expanded=self.IsPanelExpanded())
        self.loadingWheel = LoadingWheel(parent=mainCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.previewContFill = FillThemeColored(parent=mainCont, align=uiconst.TOALL)
        overlayCont = Container(name='overlayCont', parent=mainCont, padding=2, clipChildren=1)
        self.title = EveCaptionMedium(text='', parent=overlayCont, align=uiconst.TOTOP, padding=(17, 4, 17, 0), state=uiconst.UI_NORMAL)
        self.title.GetMenu = self.GetShipMenu
        self.title.expandOnLeft = 1
        self.subtitle = EveHeaderSmall(text='', parent=overlayCont, align=uiconst.TOTOP, padding=(19, 0, 17, 0), state=uiconst.UI_DISABLED)
        self.descCont = ScrollContainer(name='DescriptionContainer', parent=mainCont, align=uiconst.TOBOTTOM_PROP, height=0.3, bgColor=(0.0, 0.0, 0.0, 0.3), state=uiconst.UI_HIDDEN)
        self.previewContainer = PreviewContainer(parent=mainCont, align=uiconst.TOALL, OnStartLoading=self.OnStartLoading, OnStopLoading=self.OnStopLoading)
        self.previewContainer.navigation.OnDropData = self.OnDropData
        self.desc = Label(parent=self.descCont, padding=12, fontsize=12, align=uiconst.TOTOP)

    def IsPanelExpanded(self):
        return self.IsPanelEnabled() and settings.user.ui.Get('previewPanel', 1)

    def IsPanelEnabled(self):
        categoryID = evetypes.GetCategoryID(self.typeID)
        if categoryID in (invconst.categoryShip, invconst.categoryShipSkin):
            self.UpdateSidePanelButton(isEnabled=True)
            return True
        self.UpdateSidePanelButton(isEnabled=False)
        return False

    def UpdateSidePanelButton(self, isEnabled):
        if not hasattr(self, 'sidePanelButton'):
            return
        if not self.sidePanelButton:
            return
        if isEnabled:
            self.sidePanelButton.Enable()
        else:
            self.sidePanelButton.Disable()

    def ToggleSidePanel(self):
        isExpanded = not self.IsPanelExpanded()
        settings.user.ui.Set('previewPanel', isExpanded)
        self.UpdateSidePanel(isExpanded)

    def UpdateSidePanel(self, expanded = None):
        if expanded is None:
            expanded = settings.user.ui.Get('previewPanel', 1)
        width = self.PANEL_WIDTH if expanded else 0
        uicore.animations.MorphScalar(self.sidePanelWrapper, 'width', startVal=self.sidePanelWrapper.width, endVal=width, duration=0.3)

    def OnStartLoading(self, previewCont):
        uicore.animations.FadeIn(self.loadingWheel, duration=0.4)
        uicore.animations.FadeIn(self.previewContFill, duration=0.05, sleep=True)
        self.ClearText()

    def OnStopLoading(self, previewCont, success):
        uicore.animations.FadeOut(self.loadingWheel, duration=0.2)
        if success:
            uicore.animations.FadeOut(self.previewContFill, duration=0.4)
            self.UpdateText()

    def UpdateText(self):
        context = self.previewContainer.context
        if not hasattr(context, 'typeID'):
            return
        groupID = evetypes.GetGroupID(context.typeID)
        categoryID = evetypes.GetCategoryID(context.typeID)
        title = evetypes.GetName(context.typeID)
        if hasattr(context, 'itemID'):
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                slim = bp.GetInvItem(context.itemID)
                if slim:
                    title = slim.name
        self.title.text = title
        subtitle = ''
        if categoryID != invconst.categoryApparel:
            scene = self.previewContainer.sceneContainer.scene
            model = first_or_default(getattr(scene, 'objects', []), None)
            if model:
                radius = round(model.GetBoundingSphereRadius() * 2, 0)
                if groupID in invconst.turretModuleGroups:
                    subtitle = localization.GetByLabel('UI/Preview/ShipSubLabelNoRace', groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))
                else:
                    raceID = evetypes.GetRaceID(context.typeID)
                    try:
                        subtitle = localization.GetByLabel('UI/Preview/ShipSubLabel', raceName=get_race_name(raceID), groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))
                    except KeyError:
                        subtitle = localization.GetByLabel('UI/Preview/ShipSubLabelNoRace', groupName=evetypes.GetGroupName(context.typeID), length=FmtDist(radius))

        self.subtitle.text = subtitle
        if categoryID == invconst.categoryApparel:
            self.descCont.Show()
            description = evetypes.GetDescription(context.typeID) or ''
            description = re.sub('<b>|</b>|\\r', '', description)
            description = re.sub('\\n', '<br>', description)
            self.desc.text = description

    def GetShipMenu(self, *args):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True).filter([localization.GetByLabel('UI/Preview/Preview')])

    def OnDropData(self, dragObj, nodes):
        super(PreviewWnd, self).OnDropData(dragObj, nodes)
        node = first(nodes)
        typeID = None
        if hasattr(node, 'item') and hasattr(node.item, 'typeID'):
            typeID = node.item.typeID
        elif hasattr(node, 'typeID'):
            typeID = node.typeID
        itemID = None
        if hasattr(node, 'item') and hasattr(node.item, 'itemID'):
            itemID = node.item.itemID
        elif hasattr(node, 'itemID'):
            itemID = node.itemID
        if typeID:
            if IsPreviewable(typeID):
                self.PreviewType(typeID, itemID=itemID)
            else:
                raise UserError('PreviewNoModel')

    def PreviewType(self, typeID, subsystems = None, itemID = None, animate = True, otherTypeID = None, skin_state = None, **kwargs):
        uthread.new(self._PreviewType, typeID, subsystems, itemID, animate, otherTypeID, skin_state, **kwargs)

    def _PreviewType(self, typeID, subsystems, itemID, animate, otherTypeID = None, skin_state = None, **kwargs):
        self.typeID = typeID
        self.BringToFront()
        if evetypes.GetCategoryID(typeID) == invconst.categoryApparel:
            self.SetMinSize([320, 470])
            self.SetMaxSize([800, 950])
        else:
            self.SetMinSize([660, 320])
            self.SetMaxSize([None, None])
        if not self.IsPanelEnabled():
            uicore.animations.FadeOut(self.sidePanelButton, duration=0.3)
            self.UpdateSidePanel(expanded=False)
        if self.IsPanelEnabled():
            uicore.animations.FadeIn(self.sidePanelButton, duration=0.3)
            self.UpdateSidePanel()
        if IsModularShip(typeID):
            kv = KeyVal(typeID=typeID)
            wnd = AssembleShip.GetIfOpen('PreviewSubSystems')
            if wnd:
                wnd.UpdateShip(kv, subsystems)
            else:
                wnd = AssembleShip.Open(windowID='PreviewSubSystems', ship=kv, groupIDs=None, isPreview=True, setselected=subsystems)
            subsystems = wnd.getSubSystems()
        else:
            self.CloseSubSystemWnd()
        newScene = self.previewContainer.PreviewType(typeID, subsystems=subsystems, itemID=itemID, controller=getattr(self, 'skinController', None), otherTypeID=otherTypeID, skin_state=skin_state, **kwargs)
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
        if categoryID == invconst.categoryShip:
            self.skinPanel.SetPreviewType(typeID)
        elif categoryID == invconst.categoryShipSkin:
            skin = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(typeID)
            shipTypeID = otherTypeID if otherTypeID and otherTypeID in skin.types else skin.types[0]
            self.skinPanel.SetPreviewType(shipTypeID)
        if newScene and animate:
            self.previewContainer.AnimEntry()

    def ClearText(self):
        self.title.text = ''
        self.subtitle.text = ''
        self.desc.SetText('')
        self.descCont.Hide()

    def BringToFront(self):
        self.Maximize()
        wnd = AssembleShip.GetIfOpen(windowID='PreviewSubSystems')
        if wnd and wnd.parent.children.index(wnd) > 1:
            wnd.Maximize()

    def _OnResize(self, *args, **kw):
        self.previewContainer.UpdateViewPort()

    def CloseSubSystemWnd(self):
        AssembleShip.CloseIfOpen(windowID='PreviewSubSystems')

    def Close(self, setClosed = False, *args, **kwds):
        Window.Close(self, setClosed, *args, **kwds)
        self.CloseSubSystemWnd()

    def OnStartMinimize_(self, *args):
        self.previewContainer.Hide()

    def OnStartMaximize_(self, *args):
        self.previewContainer.Show()


class PreviewCharacterWnd(Window):
    __guid__ = 'form.PreviewCharacterWnd'
    default_windowID = 'previewCharacterWnd'
    default_minSize = (420, 320)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.CloseIfOpen()
        self.charID = attributes.charID
        self.dna = attributes.dna
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        self.btnGroup.AddButton(localization.GetByLabel('UI/Preview/ViewPortrait'), self.SwitchToPortrait, (self.charID,))
        self.previewContainer = PreviewContainer(parent=self.sr.main)
        self.PreviewCharacter(self.charID, dna=self.dna)

    def PreviewCharacter(self, charID, dna):
        self.charID = charID
        self.dna = dna
        caption = localization.GetByLabel('UI/InfoWindow/PortraitCaption', character=charID)
        self.SetCaption(caption)
        uthread.new(self.previewContainer.PreviewCharacter, charID, dna=dna)
        self.Maximize()

    def SwitchToPortrait(self, charID):
        from eve.client.script.ui.shared.portraitWindow.portraitWindow import PortraitWindow
        PortraitWindow.CloseIfOpen()
        portraitWnd = PortraitWindow.Open(charID=charID)
        portraitWnd.Maximize()
        self.CloseByUser()

    def _OnResize(self, *args, **kw):
        self.previewContainer.UpdateViewPort()


class InvalidPreviewType(Exception):
    pass


class PreviewContainerClosing(Exception):
    pass


class PreviewNavigation(SceneContainerBaseNavigation):
    default_cursor = uiconst.UICURSOR_CCALLDIRECTIONS
    default_state = uiconst.UI_NORMAL

    def UpdateCursor(self):
        if uicore.uilib.rightbtn and not uicore.uilib.leftbtn and self.sr.sceneContainer.verticalPanEnabled:
            self.cursor = uiconst.UICURSOR_CCUPDOWN
        else:
            self.cursor = uiconst.UICURSOR_CCALLDIRECTIONS

    def OnMouseDown(self, *args):
        SceneContainerBaseNavigation.OnMouseDown(self, *args)
        self.UpdateCursor()

    def OnMouseUp(self, *args):
        SceneContainerBaseNavigation.OnMouseUp(self, *args)
        self.UpdateCursor()

    def OnMouseMove(self, *args):
        if self.sr.sceneContainer.verticalPanEnabled and uicore.uilib.rightbtn:
            cameraDistance = self.sr.sceneContainer.camera.GetZoomDistance()
            delta = uicore.uilib.dy * 0.0006 * cameraDistance
            y = self.sr.sceneContainer.verticalPan
            self.sr.sceneContainer.verticalPan = y + delta
        else:
            SceneContainerBaseNavigation.OnMouseMove(self, *args)


class PreviewSceneContainer(SceneContainer):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(PreviewSceneContainer, self).ApplyAttributes(attributes)
        self._minY = None
        self._maxY = None

    @property
    def verticalPanLimits(self):
        return (self._minY, self._maxY)

    @verticalPanLimits.setter
    def verticalPanLimits(self, limits):
        if limits is None:
            limits = (None, None)
        minY, maxY = limits
        if minY > maxY:
            minY, maxY = maxY, minY
        self._minY = minY
        self._maxY = maxY

    @property
    def verticalPanEnabled(self):
        return self._minY is not None and self._maxY is not None

    @property
    def verticalPan(self):
        if self.camera:
            return self.camera.atPosition[1]

    @verticalPan.setter
    def verticalPan(self, y):
        if self.verticalPanEnabled:
            y = mathext.clamp(y, self._minY, self._maxY)
            x, _, z = self.camera.atPosition
            self.camera.SetAtPosition((x, y, z))


class PreviewContainer(Container):
    __notifyevents__ = ['OnGraphicSettingsChanged', 'OnSetDevice']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.context = None
        self.startLoadingCallback = attributes.get('OnStartLoading', None)
        self.stopLoadingCallback = attributes.get('OnStopLoading', None)
        self.skinController = None
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.loadingWheel.opacity = 0.0
        self.ConstructSceneContainer()
        self.sceneContainer.Startup()
        self.navigation = PreviewNavigation(parent=self)
        self.navigation.Startup(self.sceneContainer)

    def ConstructSceneContainer(self):
        self.sceneContainer = PreviewSceneContainer(parent=self, align=uiconst.TOALL)

    def Close(self):
        super(PreviewContainer, self).Close()
        self._Cleanup()

    def _OnStartLoading(self):
        if self.startLoadingCallback:
            self.startLoadingCallback(self)
        else:
            uicore.animations.FadeIn(self.loadingWheel, duration=0.4)

    def _OnStopLoading(self, success):
        if self.stopLoadingCallback:
            self.stopLoadingCallback(self, success)
        else:
            uicore.animations.FadeOut(self.loadingWheel, duration=0.4)

    def PreviewType(self, typeID, **kwargs):
        if not IsPreviewable(typeID):
            raise InvalidPreviewType('%s (%s) is not previewable' % (evetypes.GetName(typeID), typeID))
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
        subsystems = kwargs.get('subsystems', None)
        if categoryID == invconst.categoryApparel:
            return self.PreviewApparel(typeID, gender=kwargs.get('gender'), background=kwargs.get('background'))
        elif groupID in invconst.turretModuleGroups:
            return self.PreviewTurret(typeID, scenePath=kwargs.get('scenePath'))
        elif categoryID == invconst.categoryShip:
            return self.PreviewShip(typeID, **kwargs)
        elif categoryID == invconst.categoryShipSkin:
            return self.PreviewSkin(typeID, **kwargs)
        else:
            return self.PreviewSpaceEntity(typeID, itemID=kwargs.get('itemID', None), subsystems=subsystems, scenePath=kwargs.get('scenePath', None))

    def PreviewApparel(self, typeID, gender = None, background = None):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.CloseIfOpen()
        context = ApparelSceneContext(typeID, gender=gender, background=background)
        return self.LoadScene(context)

    def PreviewCharacter(self, charID, dna = None, apparel = None, background = None):
        context = CharacterSceneContext(charID, dna=dna, apparel=apparel, background=background)
        return self.LoadScene(context)

    def PreviewShip(self, typeID, controller = None, skin_state = None, scenePath = None, subsystems = None, **kwargs):
        skin = skin_state
        if skin_state:
            if skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                skin = sm.GetService('cosmeticsSvc').GetFirstPartySkinObject(licenseeID=skin_state.character_id, skinID=skin_state.skin_data.skin_id)
            elif skin_state.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                if skin_state.character_id == session.charid:
                    try:
                        skin_license = get_ship_skin_license_svc().get_license(license_id=skin_state.skin_data.skin_id, owner_character_id=skin_state.character_id)
                        if skin_license:
                            skin = ThirdPartySkinWrapper(skin_license)
                    except (GenericException, TimeoutException):
                        ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))

        if controller:
            controller.onChange.disconnect(self.UpdateShipEntity)
            if controller.typeID != typeID:
                controller.typeID = typeID
            if skin:
                for s in controller.skins:
                    if s == skin:
                        controller.PickSkinAndMoveToIt(s, deselectIfSame=False)
                        break

            self.skinController = controller
            controller.onChange.connect(self.UpdateShipEntity)
        self.scenePath = scenePath
        return self.PreviewShipEntity(typeID, skin=skin_state, scenePath=scenePath, subsystems=subsystems)

    def PreviewSkin(self, typeID, controller = None, scenePath = None, subsystems = None, otherTypeID = None, **kwargs):
        skin = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(typeID)
        entityTypeID = otherTypeID if otherTypeID and otherTypeID in skin.types else skin.types[0]
        if controller:
            controller.onChange.disconnect(self.UpdateSkinnedEntity)
            if controller.typeID != entityTypeID:
                controller.typeID = entityTypeID
            for s in controller.skins:
                if s.skinID == skin.skinID:
                    controller.PickSkinAndMoveToIt(s, deselectIfSame=False)
                    break

            self.skinController = controller
            controller.onChange.connect(self.UpdateSkinnedEntity)
        self.scenePath = scenePath
        return self.PreviewShipEntity(entityTypeID, skin=skin, scenePath=scenePath, subsystems=subsystems)

    def UpdateSkinnedEntity(self):
        typeID = self.skinController.typeID
        if IsShipType(typeID):
            self.UpdateShipEntity()
            return
        materialSetID = None if self.skinController.previewed is None else self.skinController.previewed.materialSetID
        uthread.new(self.PreviewSpaceEntity, typeID, materialSetID=materialSetID, scenePath=self.scenePath, subsystems=getattr(self.context, 'subsystems', None), resetZoom=False)

    def UpdateShipEntity(self):
        uthread.new(self.PreviewShipEntity, self.skinController.typeID, skin=self.skinController.previewed, scenePath=self.scenePath, subsystems=getattr(self.context, 'subsystems', None), resetZoom=False)

    def PreviewSpaceEntity(self, typeID, itemID = None, materialSetID = None, subsystems = None, scenePath = None, resetZoom = True):
        context = SpaceEntitySceneContext(typeID, itemID=itemID, materialSetID=materialSetID, subsystems=subsystems, scenePath=scenePath, resetZoom=resetZoom)
        return self.LoadScene(context)

    def PreviewShipEntity(self, typeID, skin = None, scenePath = None, subsystems = None, resetZoom = True):
        context = ShipEntitySceneContext(typeID, skin=skin, subsystems=subsystems, scenePath=scenePath, resetZoom=resetZoom)
        return self.LoadScene(context)

    def PreviewSofDna(self, dna, dirt = None, scenePath = None):
        context = SofDnaSceneContext(dna, dirt=dirt, scenePath=scenePath)
        return self.LoadScene(context)

    def PreviewTurret(self, typeID, scenePath = None):
        context = TurretSceneContext(typeID, scenePath=scenePath)
        return self.LoadScene(context)

    def LoadScene(self, context, force = False):
        if context == self.context and not force:
            return False
        success = True
        try:
            self._OnStartLoading()
            self._Cleanup()
            self.context = context
            self.context.LoadScene(self.sceneContainer)
            self.UpdateViewPort()
        except Exception:
            if not self.destroyed:
                log.LogException('Exception raised while loading preview for {context}'.format(context=str(context)))
                sys.exc_clear()
                success = False

        self._OnStopLoading(success)
        return success

    def Reload(self):
        if self.context:
            self.LoadScene(self.context, force=True)

    def _Cleanup(self):
        try:
            if self.context:
                self.context.Cleanup()
                self.context = None
        except Exception:
            log.LogException('Exception raised during preview container cleanup', severity=log.INFO)
            sys.exc_clear()

    def AnimEntry(self, yaw0 = 1.1 * math.pi, pitch0 = 0.0, yaw1 = 1.25 * math.pi, pitch1 = 0.3, duration = 2.0):
        self.sceneContainer.AnimEntry(yaw0, pitch0, yaw1, pitch1, duration)

    def UpdateViewPort(self):
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()

    def OnSetDevice(self):
        uthread.new(self.Reload)

    def OnGraphicSettingsChanged(self, changes):
        if self.context and any((setting in self.context.relevantSettings for setting in changes)):
            uthread.new(self.Reload)


class SceneContext(object):
    relevantSettings = []

    def LoadScene(self, sceneContainer):
        raise NotImplementedError('SceneContexts must override the LoadScene method')

    def Cleanup(self):
        pass


class ApparelSceneContext(SceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY]

    def __init__(self, typeID, gender = None, background = None):
        if evetypes.GetCategoryID(typeID) != invconst.categoryApparel:
            raise InvalidPreviewType('%s (%s) is not an apparel item' % (evetypes.GetName(typeID), typeID))
        self.typeID = typeID
        self.gender = gender
        self.background = background
        self.mannequin = None

    def __eq__(self, other):
        return isinstance(other, ApparelSceneContext) and self.typeID == other.typeID and self.gender == other.gender and self.background == other.background

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareInteriorScene(backgroundImage=self.background, useShadows=True)
        apparel = GetPaperDollResource(self.typeID, gender=self.gender)
        if apparel is None:
            raise InvalidPreviewType('%s (%s) does not have an associated paper doll resource' % (evetypes.GetName(self.typeID), self.typeID))
        factory = Factory()
        mannequin = PaperDollCharacter(factory)
        self.mannequin = mannequin
        dollGender = GenderIDToPaperDollGender(apparel.resGender)
        mannequin.doll = Doll('mannequin', gender=dollGender)
        mannequin.doll.Load(MANNEQUIN_RES_BY_GENDER[dollGender], factory)
        mannequin.WaitForUpdate()
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        resolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        mannequin.doll.textureResolution = resolution
        mannequin.doll.overrideLod = LOD_SKIN
        mannequin.Spawn(sceneContainer.scene)
        mannequin.WaitForUpdate()
        with CaptureDollMeshChanges(mannequin.doll) as meshes:
            modifier = mannequin.doll.SetItemType(factory, apparel.resPath)
            if 'tattoo/head' in apparel.resPath.lower():
                modifier.SetColorVariation('default_a')
            typeData = factory.GetItemType(apparel.resPath, gender=dollGender)
            apparelCategory = sm.GetService('character').GetCategoryFromResPath(typeData[0])
            coveringCategories = PAPERDOLL_CATEGORIES_COVERING.get(apparelCategory, [])
            for category in coveringCategories:
                mannequin.doll.buildDataManager.RemoveMeshContainingModifiers(category)

            mannequin.Update()
            mannequin.WaitForUpdate()
        newMeshes = set(filter(lambda m: m not in meshes.before, meshes.after))
        assetGroupID = evetypes.GetGroupID(self.typeID)
        if apparelCategory == 'makeup/bodyaugmentations':
            assetGroupID = invconst.groupApparelOuter
        if apparelCategory == 'tattoo/head':
            assetGroupID = invconst.groupApparelAugmentations
        meshNameCheck = lambda mesh: any(map(lambda name: mesh.name.startswith(name), MESH_NAMES_BY_GROUPID[assetGroupID]))
        groupMeshes = set(filter(meshNameCheck, meshes.after))
        boundingBoxes = map(lambda m: m.geometry.GetBoundingBox(0), newMeshes | groupMeshes)
        if len(boundingBoxes) == 0:
            aabb = mannequin.visualModel.GetBoundingBoxInLocalSpace()
        else:
            aabb = reduce(MergeBoundingBoxes, boundingBoxes)
        if dollGender == GENDER.FEMALE:
            animationRes = 'res:/Animation/PortraitCreator/Female/CharacterCreation/Mannequin.gr2'
        else:
            animationRes = 'res:/Animation/PortraitCreator/Male/CharacterCreation/Mannequin.gr2'
        animationUpdater = trinity.Tr2GrannyAnimation()
        animationUpdater.resPath = animationRes
        if animationUpdater is not None:
            mannequin.avatar.animationUpdater = animationUpdater
        floorShadow = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
        sceneContainer.scene.dynamics.append(floorShadow)
        SetupInteriourCamera(sceneContainer, aabb)

    def Cleanup(self):
        self.mannequin = None


class CharacterSceneContext(SceneContext):
    relevantSettings = [gfxsettings.GFX_CHAR_TEXTURE_QUALITY, gfxsettings.UI_NCC_GREEN_SCREEN, gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION]

    def __init__(self, charID, dna = None, apparel = None, background = None):
        dna = dna or sm.RemoteSvc('paperDollServer').GetPaperDollData(charID)
        if dna is None:
            raise UserError('CharacterHasNoDNA', {'charID': charID})
        self.charID = charID
        self.dna = dna
        self.apparel = apparel or []
        self.background = background
        self.boundingBox = None
        self.character = None

    def __eq__(self, other):
        return isinstance(other, CharacterSceneContext) and self.charID == other.charID and self.dna == other.dna and self.apparel == other.apparel and self.background == other.background

    def LoadScene(self, sceneContainer):
        charInfo = sm.RemoteSvc('charMgr').GetPublicInfo(self.charID)
        bloodlineID = charInfo.bloodlineID
        gender = charInfo.gender
        background = self.GetBackground()
        sceneFile = self.GetSceneFile(charInfo)
        sceneContainer.PrepareInteriorScene(useShadows=True, backgroundImage=background, sceneFile=sceneFile)
        if gender is None:
            owner = cfg.eveowners.Get(self.charID)
            raise RuntimeError('{0.name} ({0.charID}) does not have a defined gender'.format(owner))
        charSvc = sm.GetService('character')
        character = charSvc.AddCharacterToScene(charID=self.charID, scene=sceneContainer.scene, gender=GenderIDToPaperDollGender(gender), bloodlineID=bloodlineID, raceID=None, dna=self.dna, lod=LOD_SKIN, updateDoll=False)
        self.character = character
        params = animparams.GetParamsPerAvatar(character.avatar)
        self.PrepareCharacterAnimation(character.avatar, gender)
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        textureResolution = ccConst.DOLL_VIEWER_TEXTURE_RESOLUTIONS[textureQuality]
        character.doll.textureResolution = textureResolution
        useFastShader = gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        character.doll.useFastShader = useFastShader
        for typeID in self.apparel:
            apparel = GetPaperDollResource(typeID, gender=gender)
            if apparel is None:
                log.LogError('Unable to preview %s (%s) since it has no associated resource' % (evetypes.GetName(typeID), typeID))
                continue
            charSvc.ApplyTypeToDoll(self.charID, apparel.resPath, doUpdate=False)

        character.Update()
        character.WaitForUpdate()
        try:
            self.boundingBox = character.visualModel.GetBoundingBoxInLocalSpace()
        except RuntimeError:
            self.boundingBox = ((-0.5, -0.5, 0), (0.5, 0.5, 1.5))

        if useFastShader:
            sceneContainer.scene.ambientColor = (0.25, 0.25, 0.25)
        if not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            sceneContainer.scene.dynamics.append(floor)
        self.SetupCamera(sceneContainer)

    def PrepareCharacterAnimation(self, avatar, gender):
        pass

    def GetBackground(self):
        background = self.background
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            background = 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001.dds'
        return background

    def GetSceneFile(self, charInfo):
        return 'res:/Graphics/Interior/characterCreation/Preview.red'

    def SetupCamera(self, sceneContainer):
        SetupInteriourCamera(sceneContainer, self.boundingBox)

    def Cleanup(self):
        sm.GetService('character').RemoveCharacter(self.charID)


def _UpdateLighting(scene, camera, ship, alive):
    scene.nebulaIntensity = 1
    scene.sunDiffuseColor = (3, 3, 3)
    while alive:
        direction = geo2.Vec3Normalize(geo2.Vec3Subtract(camera.atPosition, camera.eyePosition))
        scene.sunDirection = direction
        uthread2.Yield()


class SpaceEntitySceneContext(SceneContext):

    def __init__(self, typeID, itemID = None, materialSetID = None, subsystems = None, scenePath = None, resetZoom = True):
        self.typeID = typeID
        self.itemID = itemID
        self.materialSetID = materialSetID
        self.subsystems = subsystems
        self.alive = []
        self.resetZoom = resetZoom
        if scenePath is None:
            hullTypeIDList = self.subsystems
            if subsystems is not None:
                hullTypeIDList = self.subsystems.values()
            modelDNA = gfxutils.BuildSOFDNAFromTypeID(self.typeID, materialSetID=self.materialSetID, multiHullTypeIDList=hullTypeIDList)
            if modelDNA is not None:
                raceName = self.GetRaceFromDNAString(modelDNA)
                scenePath = eveSpaceObject.GetPreviewScenePathByRaceName(raceName)
            else:
                scenePath = eveSpaceObject.GetPreviewScenePathByRaceName('')
        self.scenePath = scenePath

    def __eq__(self, other):
        return isinstance(other, SpaceEntitySceneContext) and self.typeID == other.typeID and self.itemID == other.itemID and self.materialSetID == other.materialSetID and self.subsystems == other.subsystems and self.scenePath == other.scenePath

    @staticmethod
    def GetRaceFromDNAString(dnaString):
        parts = dnaString.split(':')
        return parts[2]

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(scenePath=self.scenePath, resetZoom=self.resetZoom)
        resFile = inventorycommon.typeHelpers.GetGraphicFile(self.typeID)
        modelDNA = None
        if evetypes.GetCategoryID(self.typeID) == invconst.categoryStation and self.itemID:
            stations = cfg.mapSolarSystemContentCache.npcStations
            npcStation = stations.get(self.itemID, None)
            if npcStation:
                graphicID = npcStation.graphicID
                modelDNA = gfxutils.BuildSOFDNAFromGraphicID(graphicID)
        subsystems = None
        if self.subsystems is not None and len(self.subsystems) > 0:
            subsystems = self.subsystems.values()
        if modelDNA is None:
            modelDNA = gfxutils.BuildSOFDNAFromTypeID(self.typeID, materialSetID=self.materialSetID, multiHullTypeIDList=subsystems)
        if modelDNA is not None:
            spaceObjectFactory = GetSofService().spaceObjectFactory
            model = spaceObjectFactory.BuildFromDNA(modelDNA)
        else:
            model = trinity.Load(resFile)
        if model is None:
            raise InvalidPreviewType('%s (%s) failed to load associated model' % (evetypes.GetName(self.typeID), self.typeID))
        if getattr(model, 'boosters', None) is not None:
            model.boosters = None
        if getattr(model, 'modelRotationCurve', None) is not None:
            model.modelRotationCurve = None
        if getattr(model, 'modelTranslationCurve', None) is not None:
            model.modelTranslationCurve = None
        SetupAnimations(model)
        trinity.WaitForResourceLoads()
        model.FreezeHighDetailMesh()
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model, resetZoom=self.resetZoom)
        self.alive = [True]
        uthread2.StartTasklet(_UpdateLighting, sceneContainer.scene, sceneContainer.camera, model, self.alive)

    def Cleanup(self):
        del self.alive[:]


class ShipEntitySceneContext(SceneContext):

    def __init__(self, typeID, skin = None, subsystems = None, scenePath = None, resetZoom = True):
        self.typeID = typeID
        self.skin = skin
        self.subsystems = subsystems
        self.alive = []
        self.resetZoom = resetZoom
        self.scenePath = scenePath or self._GetDefaultScenePath()

    def __eq__(self, other):
        return isinstance(other, SpaceEntitySceneContext) and self.typeID == other.typeID and self.skin == other.skin and self.subsystems == other.subsystems and self.scenePath == other.scenePath

    def _GetDefaultScenePath(self):
        hullTypeIDList = self.subsystems.values() if self.subsystems else []
        modelDNA = gfxutils.BuildSOFDNAFromTypeID(self.typeID, multiHullTypeIDList=hullTypeIDList)
        if modelDNA is not None:
            raceName = self.GetRaceFromDNAString(modelDNA)
            scenePath = eveSpaceObject.GetPreviewScenePathByRaceName(raceName)
        else:
            scenePath = eveSpaceObject.GetPreviewScenePathByRaceName('')
        return scenePath

    @staticmethod
    def GetRaceFromDNAString(dnaString):
        parts = dnaString.split(':')
        return parts[2]

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(scenePath=self.scenePath, resetZoom=self.resetZoom)
        subsystems = self.subsystems.values() if self.subsystems else None
        model = GetSkinnedShipModel(skin=self.skin, typeID=self.typeID, multiHullTypeIDList=subsystems)
        if model is None:
            resFile = inventorycommon.typeHelpers.GetGraphicFile(self.typeID)
            model = trinity.Load(resFile)
        if model is None:
            raise InvalidPreviewType('%s (%s) failed to load associated model' % (evetypes.GetName(self.typeID), self.typeID))
        if getattr(model, 'boosters', None) is not None:
            model.boosters = None
        if getattr(model, 'modelRotationCurve', None) is not None:
            model.modelRotationCurve = None
        if getattr(model, 'modelTranslationCurve', None) is not None:
            model.modelTranslationCurve = None
        SetupAnimations(model)
        trinity.WaitForResourceLoads()
        model.FreezeHighDetailMesh()
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model, resetZoom=self.resetZoom)
        self.alive = [True]
        uthread2.StartTasklet(_UpdateLighting, sceneContainer.scene, sceneContainer.camera, model, self.alive)

    def Cleanup(self):
        del self.alive[:]


class SofDnaSceneContext(SceneContext):

    def __init__(self, dna, dirt = None, scenePath = None):
        if scenePath is None:
            scenePath = GetGraphicFile(20413)
        self.dna = dna
        self.dirt = dirt
        self.scenePath = scenePath
        self.model = None

    def __eq__(self, other):
        return isinstance(other, SofDnaSceneContext) and self.dna == other.dna and self.scenePath == other.scenePath and self.dirt == other.dirt

    def LoadScene(self, sceneContainer):
        try:
            sceneContainer.PrepareSpaceScene(scenePath=self.scenePath)
        except RuntimeError:
            return

        spaceObjectFactory = GetSofService().spaceObjectFactory
        model = spaceObjectFactory.BuildFromDNA(self.dna)
        self.model = model
        if model is None:
            raise InvalidPreviewType('failed to load associated model: ' + self.dna)
        if self.dirt is not None:
            model.dirtLevel = self.dirt
        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)

    def GetModel(self):
        return self.model


class TurretSceneContext(SceneContext):

    def __init__(self, typeID, scenePath = None):
        if evetypes.GetGroupID(typeID) not in invconst.turretModuleGroups:
            raise InvalidPreviewType('%s (%s) is not a turret module' % (evetypes.GetName(typeID), typeID))
        self.typeID = typeID
        self.scenePath = scenePath or 'res:/dx9/scene/fitting/previewTurrets.red'

    def __eq__(self, other):
        return isinstance(other, TurretSceneContext) and self.typeID == other.typeID and self.scenePath == other.scenePath

    def LoadScene(self, sceneContainer):
        sceneContainer.PrepareSpaceScene(maxPitch=math.pi / 2 - 0.1, scenePath=self.scenePath)
        model = trinity.Load('res:/dx9/model/ship/IconPreview/PreviewTurretShip.red')
        graphicID = evetypes.GetGraphicID(self.typeID)
        turretSet = TurretSet.FitTurret(model, self.typeID, 1, GetSofFactionName(graphicID), checkSettings=False)
        if turretSet is None:
            raise RuntimeError('Failed to load preview for %s (%s)' % (evetypes.GetName(self.typeID), self.typeID))
        boundingSphere = turretSet.turretSets[0].boundingSphere
        model.boundingSphereRadius = boundingSphere[3]
        model.boundingSphereCenter = boundingSphere[:3]
        if model.boundingSphereCenter[1] < 2.0:
            model.boundingSphereCenter = (boundingSphere[0], 2.0, boundingSphere[2])
        for turret in turretSet.turretSets:
            if 'moonharvester' not in turret.locatorName:
                turret.bottomClipHeight = 0.0
            else:
                turret.display = True
            turret.FreezeHighDetailLOD()
            turret.ForceStateDeactive()
            turret.EnterStateIdle()

        sceneContainer.AddToScene(model)
        SetupSpaceCamera(sceneContainer, model)


def SetupSpaceCamera(sceneContainer, model, resetZoom = True):
    sceneContainer.verticalPanLimits = None
    lookatOffset = GetModelLookAtOffset(model)
    camera = sceneContainer.camera
    camera.SetAtPosition(lookatOffset)
    alpha = sceneContainer.fov / 2.0
    radius = model.GetBoundingSphereRadius() + geo2.Vec3Length(lookatOffset)
    maxZoom = min(sceneContainer.backClip - radius, max(radius * (1 / math.tan(alpha)) * 2, 1.0))
    minZoom = radius + sceneContainer.frontClip
    sceneContainer.SetMinMaxZoom(minZoom, maxZoom)
    if resetZoom:
        sceneContainer.SetZoom(0.5)


def SetupInteriourCamera(sceneContainer, boundingBox):
    p0, p1 = geo2.Vector(boundingBox[0]), geo2.Vector(boundingBox[1])
    center = 0.5 * (p1 - p0) + p0
    camera = sceneContainer.camera
    camera.SetAtPosition(center)
    sceneContainer.verticalPanLimits = (p0.y, p1.y)
    rad = max(geo2.Vec3Length(p0 - p1), 0.3)
    alpha = sceneContainer.fov * 1.5 / 2.0
    maxZoom = min(rad * (1 / math.tan(alpha)), 9.0)
    minZoom = rad + sceneContainer.frontClip
    sceneContainer.SetMinMaxZoom(minZoom, maxZoom)
    camera.SetZoomLinear(0.6)
    camera.kMinPitch = 0.0
    camera.kMaxPitch = math.pi / 2.0
    camera.kOrbitSpeed = 30.0
    camera.farClip = 100.0


class CaptureDollMeshChanges(object):

    def __init__(self, doll):
        self.doll = doll

    def __enter__(self):
        self.before = self.doll.buildDataManager.GetMeshes(includeClothMeshes=True)
        return self

    def __exit__(self, type, value, traceback):
        self.after = self.doll.buildDataManager.GetMeshes(includeClothMeshes=True)


def MergeBoundingBoxes(a, b):
    merged = ((min(a[0][0], b[0][0]), min(a[0][1], b[0][1]), min(a[0][2], b[0][2])), (max(a[1][0], b[1][0]), max(a[1][1], b[1][1]), max(a[1][2], b[1][2])))
    return merged


SCHEME = 'preview'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_preview_link, hint='UI/Preview/Preview')


def handle_preview_link(url):
    type_id = parse_preview_url(url)
    sm.GetService('preview').PreviewType(type_id)


def parse_preview_url(url):
    return int(url[url.index(':') + 1:])
