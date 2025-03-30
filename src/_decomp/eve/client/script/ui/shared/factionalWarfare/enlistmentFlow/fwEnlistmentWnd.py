#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\fwEnlistmentWnd.py
from eve.client.script.ui import eveColor
import signals
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import TextCustom, TextBody, TextColor
from carbonui.control.window import Window
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
import eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil as enlistmentUtil
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.backgroundDeco import BackgroundDeco
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import SELECTED_PIRATES, SELECTED_EMPIRE, SELECTED_PAGE_FRONT, SELECTED_PAGE_FACTIONPICKER, NODE_SIZE, BG_TEXTURE_PATH_BY_SIDE, INFO_MAX_WIDTH
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.factionBanner import FactionBanner
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.factionCircle import EnlistmentCircleView, EnlistmentCenterCont
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.backBtn import BackBtnFront
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.frontPageCont import EnlistmentFrontPageCont
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.infoPicker import InfoPickerCont
from eve.common.script.util.facwarCommon import GetPirateFWFactions, IsPirateFWFaction
from eveexceptions import ExceptionEater
from jobboard.client import get_job_board_service
import eve.common.lib.appConst as appConst
from localization import GetByLabel
FACTION_CIRCLE_SIZE = 370
OUTER_CIRCLE_CONT_WIDTH = 640
INNER_CIRCLE_OFFSET = 60
INNER_CIRCLE_SIZE_BIG = 650
CIRCLE_OFFSET_PAGE2 = 500

class EnlistmentController(object):

    def __init__(self):
        self.pageSelected = SELECTED_PAGE_FRONT
        self.insurgencySideSelected = 0
        self.selectedFactionID = None
        self.hoveredFactionID = None
        self.isMovingCircle = False
        self.on_mouse_enter = signals.Signal('EnlistmentController_on_mouse_enter')
        self.on_mouse_exit = signals.Signal('EnlistmentController_on_mouse_exit')
        self.on_node_clicked = signals.Signal('EnlistmentController_on_click')
        self.on_back_mouse_enter = signals.Signal('EnlistmentController_on_back_mouse_enter')
        self.on_back_mouse_exit = signals.Signal('EnlistmentController_on_back_mouse_exit')
        self.on_empire_pirates_clicked = signals.Signal('EnlistmentController_on_empire_pirates_clicked')
        self.on_insurgency_side_mouse_enter = signals.Signal('EnlistmentController_on_insurgency_side_mouse_enter')
        self.on_insurgency_side_mouse_exit = signals.Signal('EnlistmentController_on_insurgency_side_mouse_exit')
        self.on_page_selected_updated = signals.Signal('EnlistmentController_on_page_selected_updated')
        self.trigger_page_update = signals.Signal('EnlistmentController_trigger_page_update')

    def ClearSignals(self):
        self.on_mouse_enter.clear()
        self.on_mouse_exit.clear()
        self.on_node_clicked.clear()

    def SelectInsurgencySide(self, insurgencySide):
        self.pageSelected = SELECTED_PAGE_FACTIONPICKER
        self.insurgencySideSelected = insurgencySide

    def SetHoverdFactionID(self, factionID):
        self.hoveredFactionID = factionID

    def ResetSelectedHoveredFactionID(self):
        self.selectedFactionID = None
        self.hoveredFactionID = None

    def SetFrontPageSelected(self, notify = True):
        self.pageSelected = SELECTED_PAGE_FRONT
        if notify:
            self.on_page_selected_updated()

    def SelectInsurgencySideFromFactionID(self, factionID):
        if IsPirateFWFaction(factionID):
            self.SelectInsurgencySide(SELECTED_PIRATES)
            return
        self.SelectInsurgencySide(SELECTED_EMPIRE)

    def GetTrackedFactionID(self):
        provider = get_job_board_service().get_provider(enlistmentUtil.JOB_PROVIDER)
        if not provider.is_enabled:
            return None
        trackedJobs = provider.get_tracked_jobs()
        if trackedJobs:
            return trackedJobs[0].faction_id


class FwEnlistmentWnd(Window):
    default_width = 1280
    default_height = 720
    default_windowID = 'fwEnlistmentWnd'
    default_iconNum = 'res:/ui/Texture/WindowIcons/factionalwarfare.png'
    default_captionLabelPath = 'UI/FactionWarfare/FwEnlistmentWnd'
    default_minSize = (1280, 720)
    default_fixedWidth = 1280
    default_fixedHeight = 720
    default_isStackable = False
    hasWindowIcon = False
    default_extend_content_into_header = True

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyAttributes(self, attributes):
        super(FwEnlistmentWnd, self).ApplyAttributes(attributes)
        self.header.show_caption = False
        self.circleView = None
        self.ConnectSignals()
        self.contentCont = Container(name='contentCont', parent=self.content, clipChildren=True)
        self.ConstructCircle()
        self.ConstructBackground()
        self.ContructRightCont()
        uthread2.StartTasklet(self.UpdateWnd)

    def ConnectSignals(self):
        self.enlistmentController = EnlistmentController()
        self.enlistmentController.on_mouse_enter.connect(self.OnFactionMouseEnter)
        self.enlistmentController.on_mouse_exit.connect(self.OnFactionMouseExit)
        self.enlistmentController.on_back_mouse_enter.connect(self.OnBackMouseEnter)
        self.enlistmentController.on_back_mouse_exit.connect(self.OnBackMouseExit)
        self.enlistmentController.on_node_clicked.connect(self.OnNodeClicked)
        self.enlistmentController.on_empire_pirates_clicked.connect(self.OnEmpirePiratesClicked)
        self.enlistmentController.on_page_selected_updated.connect(self.OnPageSelectedUpdated)
        self.enlistmentController.trigger_page_update.connect(self.PageUpdateTriggered)
        self.enlistmentController.on_insurgency_side_mouse_enter.connect(self.OnInsurgencySideMouseEnter)
        self.enlistmentController.on_insurgency_side_mouse_exit.connect(self.OnInsurgencySideMouseExit)
        self.on_end_scale.connect(self.OnEndScale)
        self.on_start_scale.connect(self.OnStartScale)

    def UpdateWnd(self):
        self.UpdateCircle()
        if not self.enlistmentController.selectedFactionID:
            factionIDToShow = session.warfactionid or self.enlistmentController.GetTrackedFactionID()
            if factionIDToShow:
                self.SelectFaction(factionIDToShow, animate=False)
                self.enlistmentController.SelectInsurgencySideFromFactionID(factionIDToShow)
                self.LoadNodes()
        self.UpdatePages(animate=False)

    def GetMenuMoreOptions(self):
        menuData = super(FwEnlistmentWnd, self).GetMenuMoreOptions()
        menuData.AddEntry(text='Reload', func=self.DebugReload)
        return menuData

    def ConstructBackground(self):
        self.bgCont = Container(name='bgCont', parent=self.content, align=uiconst.TOALL, clipChildren=True)
        self.decoBgCont = Container(parent=self.bgCont, name='decoBgCont')
        self.bgSpriteFrontpage = Sprite(name='bgSpriteFrontpage', parent=self.decoBgCont, align=uiconst.CENTER, pos=(0, 0, 1280, 720), opacity=0, state=uiconst.UI_DISABLED)
        self.bgSpritePage1 = Sprite(name='bgSpritePage1', parent=self.decoBgCont, align=uiconst.CENTER, pos=(0, 0, 1280, 720), opacity=0, state=uiconst.UI_DISABLED)
        self.bgSprite = Sprite(name='bgSprite', parent=self.bgCont, align=uiconst.CENTER, pos=(0, 0, 1280, 720), state=uiconst.UI_DISABLED)

    def ConstructCircle(self):
        self.outerCircleCont = Container(name='outerCircleCont', parent=self.contentCont, align=uiconst.TOLEFT, width=OUTER_CIRCLE_CONT_WIDTH)
        self.circleCont = Container(name='circleCont', parent=self.outerCircleCont, align=uiconst.CENTER, pos=(INNER_CIRCLE_OFFSET,
         0,
         INNER_CIRCLE_SIZE_BIG,
         INNER_CIRCLE_SIZE_BIG))
        self.backBtnFrontPage = BackBtnFront(parent=self.outerCircleCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         NODE_SIZE,
         NODE_SIZE), idx=0, enlistmentController=self.enlistmentController)
        from carbonui.control.button import Button
        if session.role & ROLE_PROGRAMMER:
            reloadBtn = Button(parent=self.content, label='Reload', align=uiconst.TOPLEFT, func=self.DebugReload, top=0, idx=0)
        self.ConstructFrontPage()
        self.factionContentCont = Container(name='factionContentCont', parent=self.circleCont)
        self.enlistmentCenterCont = EnlistmentCenterCont(parent=self.factionContentCont, enlistmentController=self.enlistmentController)
        self.circleView = EnlistmentCircleView(parent=self.factionContentCont, width=720, height=self.height, state=uiconst.UI_NORMAL, enlistmentController=self.enlistmentController)
        self.circleView.innerCircles.opacity = 0
        self.circleView.fill.outputMode = uiconst.OUTPUT_COLOR
        self.bgDeco = BackgroundDeco(parent=self.circleCont, align=uiconst.CENTER)

    def LoadEmpireFactions(self):
        factionIDs = [appConst.factionAmarrEmpire,
         appConst.factionCaldariState,
         appConst.factionMinmatarRepublic,
         appConst.factionGallenteFederation]
        self.circleView.LoadNodes(factionIDs)
        self.page1.UpdateHeaderAndText(GetByLabel('UI/FactionWarfare/Enlistment/FactionalWarfareHeader'), GetByLabel('UI/FactionWarfare/Enlistment/FactionalWarfareDescription'))
        self.enlistmentCenterCont.LoadCenterText(GetByLabel('UI/FactionWarfare/Enlistment/ClickOnEmpireFaction'))
        self.enlistmentCenterCont.LoadCenterIcon('res:/ui/Texture/classes/frontlines/factionalwarfare_icon.png')

    def LoadPirateFactions(self):
        factionIDs = GetPirateFWFactions()
        self.circleView.LoadNodes(factionIDs)
        self.page1.UpdateHeaderAndText(GetByLabel('UI/FactionWarfare/Enlistment/PiratesHeader'), GetByLabel('UI/FactionWarfare/Enlistment/PiratesDescription'))
        self.enlistmentCenterCont.LoadCenterText(GetByLabel('UI/FactionWarfare/Enlistment/ClickOnPirateFaction'))
        self.enlistmentCenterCont.LoadCenterIcon('res:/UI/Texture/eveicon/theatres_of_war/pirates_64px.png')

    def OnFactionMouseEnter(self, factionID):
        self.enlistmentController.SetHoverdFactionID(factionID)
        self.UpdateDecoColor()
        self.circleView.UpdateFaction()
        self.page1.UpdateFaction(factionID)
        self.enlistmentCenterCont.ShowFaction(factionID)
        self.UpdateBackgroundSprites(True)

    def OnFactionMouseExit(self, factionID):
        self.enlistmentController.SetHoverdFactionID(None)
        self.UpdateDecoColor()
        self.circleView.UpdateFaction()
        self.page1.UpdateFaction(None)
        self.page2.UpdateFaction(None)
        self.enlistmentCenterCont.ShowFaction(None)
        self.UpdateBackgroundSprites(True)

    def UpdateDecoColor(self):
        factionID = self.enlistmentController.selectedFactionID or self.enlistmentController.hoveredFactionID
        decoColor = enlistmentUtil.GetFactionColor(factionID) or eveColor.CRYO_BLUE
        self.bgDeco.ColorSprites(decoColor)
        return decoColor

    def OnBackMouseEnter(self):
        if self.enlistmentController.selectedFactionID and not self.enlistmentController.isMovingCircle:
            self.UpdateLeft(offset=20, duration=0.1)

    def OnBackMouseExit(self):
        if self.enlistmentController.selectedFactionID and not self.enlistmentController.isMovingCircle:
            self.UpdateLeft(offset=0.0, duration=0.1)

    def OnNodeClicked(self, factionID):
        self.SelectFaction(factionID)

    def SelectFaction(self, factionID, animate = True):
        if self.enlistmentController.selectedFactionID == factionID:
            self.enlistmentController.selectedFactionID = None
            self.enlistmentCenterCont.ShowFaction(None)
        else:
            self.enlistmentController.selectedFactionID = factionID
            self.enlistmentCenterCont.ShowFaction(factionID)
        self.UpdatePages(animate=animate)

    def ConstructFrontPage(self):
        self.frontPage = EnlistmentFrontPageCont(parent=self.circleCont, align=uiconst.TOALL, enlistmentController=self.enlistmentController)
        self.frontPage.Hide()

    def ContructRightCont(self):
        self.rightCont = Container(name='rightCont', parent=self.contentCont, align=uiconst.TOALL)
        self.page1 = EnlistmentPage1(parent=self.rightCont, align=uiconst.TOALL, padLeft=180)
        self.page2 = EnlistmentPage2(parent=self.rightCont, align=uiconst.TOALL, padLeft=0)
        self.page2.Hide()

    def UpdateLeft(self, animate = True, offset = 0.0, duration = enlistmentUtil.ANIM_DURATION):
        factionID = self.enlistmentController.selectedFactionID
        newCircleLeft = -CIRCLE_OFFSET_PAGE2 if factionID else 0
        newCircleLeft = newCircleLeft + offset
        self.enlistmentController.hoveredFactionID = None
        if animate:
            self.enlistmentController.isMovingCircle = True
            animations.MorphScalar(self.outerCircleCont, 'left', self.outerCircleCont.left, newCircleLeft, duration=duration, callback=self.OnMovingFinished)
        else:
            self.outerCircleCont.left = newCircleLeft
            self.enlistmentController.isMovingCircle = False

    def OnMovingFinished(self):
        self.enlistmentController.isMovingCircle = False
        self.circleView.MovingFinished()
        self.UpdateDecoColor()

    def PageUpdateTriggered(self, animate = False):
        self.UpdatePages(animate)

    def UpdatePages(self, animate = True):
        if self.enlistmentController.pageSelected == SELECTED_PAGE_FRONT:
            return self.UpdatePagesFrontVisible(animate)
        self.UpdatePagesFactionsVisible(animate)

    def UpdatePagesFrontVisible(self, animate):
        self.bgDeco.SetMainCircleSize(True, animate)
        self.frontPage.Show()
        self.backBtnFrontPage.Hide()
        self.backBtnFrontPage.opacity = 0.0
        newCircleContWidth = self.width
        newCircleLeft = -INNER_CIRCLE_OFFSET
        self.bgSpriteFrontpage.Show()
        if animate:
            animations.FadeOut(self.rightCont, callback=self.rightCont.Hide)
            animations.FadeOut(self.factionContentCont, callback=self.factionContentCont.Hide)
            animations.FadeIn(self.frontPage, duration=0.5, timeOffset=0.25)
            self.enlistmentController.isMovingCircle = True
            animations.MorphScalar(self.outerCircleCont, 'left', self.outerCircleCont.left, newCircleLeft)
            animations.MorphScalar(self.outerCircleCont, 'width', self.outerCircleCont.width, newCircleContWidth, callback=self.OnMovingFinished)
        else:
            self.rightCont.Hide()
            self.factionContentCont.Hide()
            self.factionContentCont.opacity = 0.0
            self.outerCircleCont.width = newCircleContWidth
            self.outerCircleCont.left = newCircleLeft
            self.frontPage.opacity = 1.0
            self.enlistmentController.isMovingCircle = False

    def UpdatePagesFactionsVisible(self, animate):
        self.factionContentCont.Show()
        self.backBtnFrontPage.Show()
        self.bgSpriteFrontpage.Hide()
        newCircleContWidth = OUTER_CIRCLE_CONT_WIDTH
        self.rightCont.Show()
        self.rightCont.opacity = 1.0
        if animate:
            animations.FadeIn(self.factionContentCont, duration=0.5, timeOffset=0.25)
            animations.FadeIn(self.backBtnFrontPage, duration=0.5, timeOffset=0.75)
            animations.MorphScalar(self.outerCircleCont, 'width', self.outerCircleCont.width, newCircleContWidth)
            animations.FadeOut(self.frontPage, callback=self.frontPage.Hide)
        else:
            self.factionContentCont.opacity = 1.0
            self.backBtnFrontPage.opacity = 1.0
            self.outerCircleCont.width = newCircleContWidth
            self.frontPage.Hide()
            self.frontPage.opacity = 0.0
        self.bgDeco.SetMainCircleSize(False, animate)
        if animate:
            self.bgDeco.Animate()
        self.UpdateLeft(animate)
        factionID = self.enlistmentController.selectedFactionID
        factionIdSet = bool(factionID)
        self.page1.ChangeDisplay(showPage=not factionIdSet, animate=animate)
        self.page1.UpdateFaction(factionID)
        self.page2.ChangeDisplay(showPage=factionIdSet, animate=animate)
        self.page2.UpdateFaction(factionID)
        self.UpdateBackgroundSprites(animate)
        self.circleView.UpdateFaction(animate)
        self.UpdateDecoColor()

    def OnStartScale(self, wnd):
        animations.FadeOut(self.outerCircleCont, duration=1.0)

    def OnEndScale(self, wnd):
        animations.FadeIn(self.outerCircleCont)
        self.UpdateCircle()

    def UpdateCircle(self):
        if self.circleView:
            self.circleView.width = self.circleView.height = FACTION_CIRCLE_SIZE + self.circleView.GetNodeSize()
            self.circleView.UpdateCircle()
            self.outerCircleCont.width = OUTER_CIRCLE_CONT_WIDTH

    def UpdateBackgroundSprites(self, animate):
        self.UpdateFactionBg(animate)
        self.UpdateMapBg(animate)

    def UpdateFactionBg(self, animate):
        factionID = self.enlistmentController.selectedFactionID
        texturePath = enlistmentUtil.GetBgTexturePath(factionID)
        self._UpdateBg(bool(factionID), self.bgSprite, texturePath, animate)

    def _UpdateBg(self, show, sprite, texturePath, animate, fullOpacity = 1.0):
        if animate:
            if show:
                self._SetBgBackground(sprite, texturePath)
                sprite.texturePath = texturePath
                animations.FadeIn(sprite, endVal=fullOpacity, duration=1.0)
            else:
                animations.FadeOut(sprite, duration=0.5, callback=lambda *args: self._SetBgBackground(sprite, texturePath))
        else:
            self._SetBgBackground(sprite, texturePath)
            if show:
                sprite.opacity = fullOpacity
            else:
                sprite.opacity = 0.0

    def _SetBgBackground(self, sprite, texturePath):
        sprite.texturePath = texturePath

    def UpdateMapBg(self, animate):
        factionID = self.enlistmentController.hoveredFactionID
        texturePath = enlistmentUtil.GetMapBgTexturePath(factionID)
        self._UpdateBg(bool(factionID), self.bgSpritePage1, texturePath, animate, fullOpacity=enlistmentUtil.BG_MAP_OPACITY)

    def OnEmpirePiratesClicked(self):
        self.bgDeco.Animate(True)
        self.LoadNodes()
        self.UpdateSection(animate=True)
        self.UpdatePages(animate=True)

    def LoadNodes(self):
        if self.enlistmentController.insurgencySideSelected == SELECTED_PIRATES:
            self.LoadPirateFactions()
        else:
            self.LoadEmpireFactions()

    def OnPageSelectedUpdated(self):
        self.UpdateSection(animate=True)

    def UpdateSection(self, animate = False):
        currentSelection = self.enlistmentController.pageSelected
        if currentSelection == SELECTED_PAGE_FRONT:
            if animate:
                self.factionContentCont.Hide()
                self.frontPage.Show()
            else:
                self.factionContentCont.Hide()
                self.frontPage.Show()
        elif currentSelection == SELECTED_PAGE_FACTIONPICKER:
            self.frontPage.Hide()
            self.factionContentCont.Show()

    def GoBackToFrontPage(self, *args):
        self.enlistmentController.ResetSelectedHoveredFactionID()
        self.enlistmentController.pageSelected = SELECTED_PAGE_FRONT
        self.UpdateFactionBg(animate=False)
        self.UpdateSection()

    def Close(self, *args, **kwds):
        with ExceptionEater('Close: FwEnlistmentWnd'):
            self.enlistmentController.ClearSignals()
            self.on_end_scale.disconnect(self.OnEndScale)
            self.on_start_scale.disconnect(self.OnStartScale)
        self.enlistmentController = None
        super(FwEnlistmentWnd, self).Close(*args, **kwds)

    def OnInsurgencySideMouseEnter(self, insurgencySideID):
        texturePath = BG_TEXTURE_PATH_BY_SIDE.get(insurgencySideID, '')
        self._UpdateBg(True, self.bgSpriteFrontpage, texturePath, True)

    def OnInsurgencySideMouseExit(self, insurgencySideID):
        self._UpdateBg(False, self.bgSpriteFrontpage, '', True)


class EnlistmentPage1(Container):
    default_name = 'EnlistmentPage1'

    def ApplyAttributes(self, attributes):
        super(EnlistmentPage1, self).ApplyAttributes(attributes)
        self.textCont = ContainerAutoSize(name='textCont', parent=self, align=uiconst.CENTERLEFT)
        grid = LayoutGrid(parent=self.textCont, align=uiconst.TOPLEFT, columns=1)
        self.headerLabel = TextCustom(name='headerLabel', parent=grid, text='', align=uiconst.TOPLEFT, fontsize=34)
        self.descLabel = TextBody(name='descLabel', parent=grid, text='', align=uiconst.TOPLEFT, maxWidth=360, color=TextColor.NORMAL)
        factionContParent = Container(parent=self, align=uiconst.TOBOTTOM_PROP, height=0.6)
        self.factionCont = FactionInfoCont(parent=factionContParent)

    def UpdateHeaderAndText(self, headerText, descText):
        self.headerLabel.text = headerText
        self.descLabel.text = descText

    def UpdateFaction(self, factionID):
        if factionID:
            self.textCont.Hide()
            self.factionCont.LoadFaction(factionID)
            self.factionCont.Show()
        else:
            self.textCont.Show()
            self.factionCont.Hide()

    def ChangeDisplay(self, showPage, animate = True):
        if animate:
            if showPage:
                self.Show()
                animations.FadeIn(self)
                endVal = TextColor.NORMAL[3]
                animations.FadeIn(self.descLabel, endVal=endVal, duration=1.0, timeOffset=0.1)
            else:
                animations.FadeOut(self, callback=self.Hide)
                animations.FadeOut(self.descLabel)
        elif showPage:
            self.Show()
        else:
            self.Hide()


class EnlistmentPage2(Container):
    default_name = 'EnlistmentPage2'
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(EnlistmentPage2, self).ApplyAttributes(attributes)
        self.ConstructFactionBanner()
        self.ConstructInfoCont()

    def ConstructInfoCont(self):
        factionContParent = Container(parent=self, align=uiconst.TOBOTTOM_PROP, height=0.6)
        self.infoCont = FactionInfoCont(parent=factionContParent)
        self.infoPickerCont = InfoPickerCont()
        self.infoCont.AddCell(self.infoPickerCont)

    def ConstructFactionBanner(self):
        self.factionBanner = FactionBanner(parent=self, align=uiconst.TORIGHT, opacity=0.0)

    def UpdateFaction(self, factionID):
        if factionID:
            self.infoCont.Show()
            self.factionBanner.Show()
            self.factionBanner.LoadFactionID(factionID)
            self.infoCont.LoadFaction(factionID)
            self.infoPickerCont.UpdateFaction(factionID)
        else:
            self.infoCont.Hide()
            self.factionBanner.Hide()
            self.infoPickerCont.UpdateFaction(None)

    def ChangeDisplay(self, showPage, animate = True):
        wasVisible = self.display
        if animate:
            if showPage:
                self.Show()
                animations.FadeIn(self)
                animations.MorphScalar(self.factionBanner, 'left', -self.factionBanner.width, 0)
                animations.FadeIn(self.factionBanner, duration=2.0)
                if not wasVisible:
                    self.infoCont.AnimateIn()
                    animations.FadeTo(self.infoPickerCont, duration=2.0)
            else:
                animations.FadeOut(self, callback=self.Hide)
                self.factionBanner.opacity = 0.0
        elif showPage:
            self.Show()
            self.factionBanner.left = 0
            self.factionBanner.opacity = 1.0
        else:
            self.Hide()
            self.factionBanner.opacity = 0.0


class FactionInfoCont(LayoutGrid):
    default_columns = 1
    align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(FactionInfoCont, self).ApplyAttributes(attributes)
        Container(name='spacer', parent=self, pos=(0,
         0,
         INFO_MAX_WIDTH,
         0), align=uiconst.TOPLEFT)
        self.factionNameLabel = TextCustom(name='factionNameLabel', parent=self, fontsize=56, align=uiconst.TOPLEFT, uppercase=True, bold=True, maxWidth=450)
        self.factionMottoLabel = TextCustom(name='factionNameLabel', parent=self, fontsize=24, align=uiconst.TOPLEFT, uppercase=True)

    def LoadFaction(self, factionID):
        self.factionNameLabel.text = cfg.eveowners.Get(factionID).name
        mottoPath = enlistmentUtil.mottoPathByFactionID.get(factionID, '')
        self.factionMottoLabel.text = GetByLabel(mottoPath)

    def AnimateIn(self):
        animations.MorphScalar(self.factionNameLabel, 'left', 190, 0)
        animations.MorphScalar(self.factionMottoLabel, 'left', 190, 0)
