#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\BasePinContainer.py
import carbonui.const as uiconst
import dogma.const
import dogma.data
import eve.common.script.util.planetCommon as planetCommon
import evetypes
import inventorycommon.const as invconst
import localization
import utillib
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import Density, fontconst, TextColor
from carbonui.control.button import Button
from carbonui.button.const import HEIGHT_COMPACT
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.services.setting import CharSettingNumeric
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from dogma.attributes.format import GetFormatAndValue, FormatUnit
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, Label
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.client.script.ui.shared.planet.planetConst import GetPinNameShort
from eve.client.script.ui.shared.planet.planetItemEntry import PlanetItemEntry
from eveexceptions import UserError
from localization import GetByLabel
HEIGHT_SETTING_KEY = 'PiActionContainerHeight_%s'

class BasePinContainer(Window):
    __notifyevents__ = ['OnRefreshPins', 'ProcessColonyDataSet']
    default_width = 600
    default_minSize = (300, 185)
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_isCollapseable = False
    default_isLightBackground = True
    default_isStackable = False
    default_isMinimizable = False
    default_isOverlayable = False
    default_windowID = 'PlanetPinWindow'
    INFO_CONT_HEIGHT = 70
    panelIDs = [planetCommonUI.PANEL_STATS,
     planetCommonUI.PANEL_LINKS,
     planetCommonUI.PANEL_ROUTES,
     planetCommonUI.PANEL_DECOMMISSION]
    createRouteBtn = None

    def GetBaseHeight(self):
        _, content_height = self.main.GetAbsoluteSize()
        _, height = self.GetWindowSizeForContentSize(height=content_height)
        return height

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        panelID = attributes.panelID
        self.planetUISvc = sm.GetService('planetUI')
        self.planetSvc = sm.GetService('planetSvc')
        self.pin = attributes.Get('pin', None)
        self.showingActionContainer = False
        self.currentRoute = None
        self.showNext = None
        self.panelID = None
        self.commodityToRoute = None
        self.buttonTextValue = ''
        self.panelFuncsByID = self._GetPanelFuncsByID()
        self.buttonsByID = {}
        self.main = ContainerAutoSize(parent=self.sr.main, name='main', padding=3, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=self._on_main_size_changed, only_use_callback_when_size_changes=True)
        infoCont = Container(parent=self.main, name='infoCont', padding=5, align=uiconst.TOTOP, height=self.INFO_CONT_HEIGHT * fontconst.fontSizeFactor)
        self.infoContLeft = Container(name='leftCol', parent=infoCont, align=uiconst.TOLEFT_PROP, width=0.5, padRight=6)
        self.infoContRight = Container(name='rightCol', parent=infoCont, align=uiconst.TOLEFT_PROP, width=0.5)
        self._GetInfoCont()
        self._UpdateInfoCont()
        self.buttonCont = GridContainer(parent=self.main, name='buttonCont', height=40, align=uiconst.TOTOP, padding=(-1, 0, -1, 0))
        PanelUnderlay(bgParent=self.buttonCont)
        self.buttonCont.lines = 1
        self.buttonCont.columns = 6
        self.buttonTextCont = self._DrawAlignTopCont(22, 'buttonTextCont')
        self.buttonText = EveLabelSmall(parent=self.buttonTextCont, align=uiconst.CENTER, color=(1.0, 1.0, 1.0, 1.0), state=uiconst.UI_NORMAL)
        self.buttonTextCont.height = max(22, self.buttonText.textheight)
        self.actionCont = Container(parent=self.sr.main, name='actionCont', padding=(6, 0, 6, 6))
        self.SetCaption(self._GetPinName())
        self.LoadActionButtons()
        uicore.animations.FadeTo(self, 0.0, 1.0, duration=0.3)
        self.updateInfoContTimer = AutoTimer(100, self._UpdateInfoCont)
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_open_play')
        self.UpdateWindowHeight(animate=False)
        if panelID and panelID in self.panelIDs:
            self.ShowPanel(panelID)

    def GetID(self):
        return self.pin.id

    def ShowDefaultPanel(self):
        if hasattr(self, 'defaultPanelID'):
            self.ShowPanel(self.defaultPanelID)

    def _GetPinName(self):
        return planetCommon.GetGenericPinName(self.pin.typeID, self.pin.id)

    def _GetInfoCont(self):
        pass

    def _GetPanelFuncsByID(self):
        return {planetCommonUI.PANEL_STATS: self.PanelShowStats,
         planetCommonUI.PANEL_LINKS: self.PanelShowLinks,
         planetCommonUI.PANEL_ROUTES: self.PanelShowRoutes,
         planetCommonUI.PANEL_DECOMMISSION: self.PanelDecommissionPin,
         planetCommonUI.PANEL_UPGRADE: self.PanelUpgrade,
         planetCommonUI.PANEL_LAUNCH: self.PanelLaunch,
         planetCommonUI.PANEL_STORAGE: self.PanelShowStorage,
         planetCommonUI.PANEL_PRODUCTS: self.PanelShowProducts,
         planetCommonUI.PANEL_SCHEMATICS: self.PanelShowSchematics,
         planetCommonUI.PANEL_SURVEYFORDEPOSITS: self.OpenSurveyWindow,
         planetCommonUI.PANEL_UPGRADELINK: self.PanelUpgrade,
         planetCommonUI.PANEL_TRANSFER: self.PanelSelectTransferDest,
         planetCommonUI.PANEL_CREATEROUTE: self.PanelCreateRoute}

    def OpenSurveyWindow(self):
        pass

    def PanelShowSchematics(self):
        pass

    def PanelLaunch(self):
        pass

    def PanelUpgrade(self):
        pass

    def ShowPanel(self, panelID, *args):
        self._UpdateSelectedButton(panelID)
        _, label = planetCommonUI.PANELDATA[panelID]
        name = localization.GetByLabel(label)
        self.buttonText.text = name
        self.buttonTextValue = name
        if self.showingActionContainer:
            self.showNext = panelID
            return
        self.showNext = None
        self.showingActionContainer = True
        self.actionCont.Flush()
        if self.panelID != panelID:
            func = self.panelFuncsByID[panelID]
            if args:
                cont = func(*args)
            else:
                cont = func()
            if cont:
                cont.state = uiconst.UI_HIDDEN
                self.panelID = panelID
                cont.opacity = 0.0
                self.ResizeActionCont(panelID)
                cont.state = uiconst.UI_PICKCHILDREN
                animations.FadeIn(cont, duration=0.25)
                uicore.registry.SetFocus(cont)
        else:
            self.HideCurrentPanel()
        self.showingActionContainer = False
        if self.showNext:
            self.ShowPanel(self.showNext)

    def _UpdateSelectedButton(self, panelID):
        oldBtn = self.buttonsByID.get(self.panelID, None)
        if oldBtn:
            oldBtn.SetDeselected()
        btn = self.buttonsByID.get(panelID, None)
        if btn:
            btn.SetSelected()

    def HideCurrentPanel(self):
        self.actionCont.Flush()
        self.UpdateWindowHeight()
        self._UpdateSelectedButton(None)
        self.panelID = None
        self.buttonTextValue = ''

    def _DrawAlignTopCont(self, height, name, padding = (0, 0, 0, 0), state = uiconst.UI_PICKCHILDREN):
        return Container(parent=self.main, name=name, pos=(0,
         0,
         0,
         height), padding=padding, state=state, align=uiconst.TOTOP)

    def OnIconButtonMouseEnter(self, iconButton, *args):
        ButtonIcon.OnMouseEnter(iconButton, *args)
        self.buttonText.text = iconButton.name

    def OnIconButtonMouseExit(self, iconButton, *args):
        ButtonIcon.OnMouseExit(iconButton, *args)
        self.buttonText.text = self.buttonTextValue

    def LoadActionButtons(self):
        iconSize = 32
        w = self.width - 6
        maxIcons = 7.0
        numButtons = len(self.panelIDs)
        n = float(numButtons)
        pad = 5 + 1 * iconSize * (1.0 - n / maxIcons)
        w -= 2 * pad
        self.buttonCont.columns = numButtons
        for i, panelID in enumerate(self.panelIDs):
            iconPath, cerberusPath = planetCommonUI.PANELDATA[panelID]
            panelName = localization.GetByLabel(cerberusPath)
            if i == 0:
                self.defaultPanel = self.panelFuncsByID[panelID]
                self.defaultPanelID = panelID
            cont = Container(name=panelName, parent=self.buttonCont)
            btn = ButtonIcon(texturePath=iconPath, parent=cont, align=uiconst.CENTER, name=panelName, width=iconSize, height=iconSize, iconSize=iconSize, func=self._OnIconButtonClicked, args=(panelID,))
            btn.OnMouseEnter = (self.OnIconButtonMouseEnter, btn)
            btn.OnMouseExit = (self.OnIconButtonMouseExit, btn)
            self.buttonsByID[panelID] = btn

    def _OnIconButtonClicked(self, panelID, *args):
        self.ShowPanel(panelID)

    def CloseByUser(self, *args):
        self.planetUISvc.eventManager.DeselectCurrentlySelected()

    def PanelShowLinks(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.linkScroll = Scroll(parent=cont, name='linksScroll', align=uiconst.TOALL)
        self.linkScroll.sr.id = 'planetBasePinLinkScroll'
        self.LoadLinkScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateNew'), self._CreateNewLink, None], [localization.GetByLabel('UI/PI/Common/DeleteLink'), self._DeleteLink, None]]
        ButtonGroup(btns=btns, idx=0, parent=cont)
        return cont

    def LoadLinkScroll(self):
        scrolllist = []
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        colony = planet.GetColony(session.charid)
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            linkedPin = colony.GetPin(linkedPinID)
            distance = link.GetDistance()
            bandwidthUsed = link.GetBandwidthUsage()
            percentageUsed = 100 * (bandwidthUsed / link.GetTotalBandwidth())
            data = utillib.KeyVal()
            data.label = '%s<t>%s<t>%s' % (planetCommon.GetGenericPinName(linkedPin.typeID, linkedPin.id), FmtDist(distance), localization.GetByLabel('UI/Common/Percentage', percentage=percentageUsed))
            data.Set('sort_%s' % localization.GetByLabel('UI/PI/Common/CapacityUsed'), percentageUsed)
            data.hint = ''
            data.OnMouseEnter = self.OnLinkEntryHover
            data.OnMouseExit = self.OnLinkEntryExit
            data.OnDblClick = self.OnLinkListentryDblClicked
            data.id = (link.endpoint1.id, link.endpoint2.id)
            sortBy = linkedPinID
            scrolllist.append((sortBy, GetFromClass(Generic, data)))

        scrolllist = SortListOfTuples(scrolllist)
        self.linkScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoLinksPresent'), headers=[localization.GetByLabel('UI/PI/Common/Destination'), localization.GetByLabel('UI/Common/Distance'), localization.GetByLabel('UI/PI/Common/CapacityUsed')])

    def IsSomeProductUnrouted(self):
        colonyData = self._GetColonyData()
        if colonyData:
            return colonyData.IsSomeProductUnrouted(self.pin.id)

    def IsSomeConsumableUnfulfilled(self):
        colonyData = self._GetColonyData()
        if colonyData:
            return colonyData.IsSomeConsumableUnfulfilled(self.pin.id)

    def _GetColonyData(self):
        colony = sm.GetService('planetUI').planet.GetColony(session.charid)
        if colony:
            return colony.colonyData

    def OnLinkListentryDblClicked(self, entry):
        myPinManager = sm.GetService('planetUI').myPinManager
        linkID = entry.sr.node.id
        link = myPinManager.linksByPinIDs[linkID]
        for node in self.linkScroll.GetNodes():
            myPinManager.RemoveHighlightLink(node.id)

        sm.GetService('planetUI').eventManager.SelectLink(link.linkGraphicID1)

    def OnLinkEntryHover(self, entry):
        node = entry.sr.node
        self.planetUISvc.myPinManager.HighlightLink(self.pin.id, node.id)

    def OnLinkEntryExit(self, entry):
        node = entry.sr.node
        self.planetUISvc.myPinManager.RemoveHighlightLink(node.id)

    def _CreateNewLink(self, *args):
        self.planetUISvc.myPinManager.SetLinkParent(self.pin.id)
        self.CloseByUser()

    def _DeleteLink(self, *args):
        selected = self.linkScroll.GetSelected()
        if len(selected) > 0:
            self.planetUISvc.myPinManager.RemoveLink(selected[0].id)
            self.LoadLinkScroll()

    def ResizeActionCont(self, panelID = None):
        if panelID:
            minHeight, maxHeight = planetCommonUI.PANEL_MIN_MAX_HEIGHT[panelID]
            if maxHeight:
                height = (minHeight + maxHeight) / 2
            else:
                heightSetting = CharSettingNumeric(HEIGHT_SETTING_KEY % panelID, minHeight, minHeight, 1000)
                height = heightSetting.get()
        else:
            height = minHeight = maxHeight = 0
        self.UpdateWindowHeight(height, minHeight, maxHeight)

    def _on_main_size_changed(self):
        self.ResizeActionCont(self.panelID)

    def OnEndScale_(self, *etc):
        if self.panelID is None:
            return
        minHeight, maxHeight = planetCommonUI.PANEL_MIN_MAX_HEIGHT[self.panelID]
        if maxHeight:
            return
        newHeight = self.height - self.GetBaseHeight()
        heightSetting = CharSettingNumeric(HEIGHT_SETTING_KEY % self.panelID, minHeight, minHeight, 1000)
        heightSetting.set(newHeight)

    def UpdateWindowHeight(self, height = 0, minHeight = 0, maxHeight = 0, animate = True):
        baseHeight = self.GetBaseHeight()
        newHeight = height + baseHeight
        if animate:
            uicore.animations.MorphScalar(self, 'height', self.height, newHeight, duration=0.3)
        else:
            self.height = newHeight
        self.SetMinSize((self.default_minSize[0] * fontconst.fontSizeFactor, baseHeight + minHeight))
        if minHeight == maxHeight:
            self.SetFixedHeight(baseHeight + minHeight)
        elif maxHeight:
            self.SetFixedHeight(None)
            self.SetMaxSize((self.default_maxSize[0], baseHeight + maxHeight))
        else:
            self.SetFixedHeight(None)
            self.SetMaxSize((self.default_maxSize[0], None))

    def _UpdateInfoCont(self):
        pass

    def PanelShowStorage(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.storageContentScroll = Scroll(parent=cont, name='storageContentsScroll', id='planetStorageContentsScroll')
        self.storageContentScroll.sr.fixedColumns = {'': 28}
        self.LoadStorageContentScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateRoute'), self._CreateRoute, 'storageContentScroll'], [localization.GetByLabel('UI/PI/Common/ExpeditedTransfer'), self._CreateTransfer, None]]
        self.createRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        return cont

    def LoadStorageContentScroll(self):
        scrolllist = []
        for typeID, amount in self.pin.contents.iteritems():
            volume = evetypes.GetVolume(typeID) * amount
            volume = GetByLabel('UI/InfoWindow/ValueAndUnit', value=volume, unit=FormatUnit(dogma.const.unitVolume))
            sortBy = amount
            scrolllist.append((sortBy, GetFromClass(PlanetItemEntry, {'label': '<t>%s<t>%s<t>%s' % (evetypes.GetName(typeID), amount, volume),
              'amount': amount,
              'typeID': typeID,
              'itemID': None,
              'getIcon': True,
              'OnDblClick': self.OnStorageEntryDblClicked})))

        scrolllist = SortListOfTuples(scrolllist)
        self.storageContentScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoContentsPresent'), headers=['',
         localization.GetByLabel('UI/PI/Common/Type'),
         localization.GetByLabel('UI/Common/Amount'),
         localization.GetByLabel('UI/Common/Volume')])

    def OnStorageEntryDblClicked(self, entry):
        self._CreateRoute('storageContentScroll')

    def PanelShowProducts(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.productScroll = Scroll(parent=cont, name='productsScroll')
        self.productScroll.sr.id = 'planetBasePinProductScroll'
        self.LoadProductScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateRoute'), self._CreateRoute, 'productScroll']]
        self.createRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        btns = [[localization.GetByLabel('UI/PI/Common/DeleteRoute'), self._DeleteRoute, ()]]
        self.deleteRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        self.createRouteButton.state = uiconst.UI_HIDDEN
        self.deleteRouteButton.state = uiconst.UI_HIDDEN
        return cont

    def LoadProductScroll(self):
        routesByTypeID = self._GetRoutesByTypeID()
        scrolllist = []
        for typeID, amount in self.pin.GetProductMaxOutput().iteritems():
            typeName = evetypes.GetName(typeID)
            for route in routesByTypeID.get(typeID, []):
                qty = route.GetQuantity()
                amount -= qty
                scrolllist.append(GetFromClass(Item, {'label': '%s<t>%s<t>%s<t>%s' % ('',
                           qty,
                           typeName,
                           localization.GetByLabel('UI/PI/Common/Routed')),
                 'typeID': typeID,
                 'itemID': None,
                 'getIcon': True,
                 'routeID': route.routeID,
                 'OnMouseEnter': self.OnRouteEntryHover,
                 'OnMouseExit': self.OnRouteEntryExit,
                 'OnClick': self.OnProductEntryClicked,
                 'OnDblClick': self.OnProductEntryDblClicked}))

            if amount > 0:
                scrolllist.append(GetFromClass(Item, {'label': '%s<t>%s<t>%s<t><color=red>%s</color>' % ('',
                           amount,
                           evetypes.GetName(typeID),
                           localization.GetByLabel('UI/PI/Common/NotRouted')),
                 'typeID': typeID,
                 'amount': amount,
                 'itemID': None,
                 'getIcon': True,
                 'OnClick': self.OnProductEntryClicked,
                 'OnDblClick': self.OnProductEntryDblClicked}))

        self.productScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoProductsPresent'), headers=['',
         localization.GetByLabel('UI/Common/Amount'),
         localization.GetByLabel('UI/PI/Common/Type'),
         localization.GetByLabel('UI/Generic/Status')])

    def _GetRoutesByTypeID(self):
        colony = self.planetUISvc.planet.GetColony(session.charid)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Cannot load product scroll for pin on a planet that has no colony')
        sourcedRoutes = colony.colonyData.GetSourceRoutesForPin(self.pin.id)
        routesByTypeID = {}
        for route in sourcedRoutes:
            typeID = route.GetType()
            if typeID not in routesByTypeID:
                routesByTypeID[typeID] = []
            routesByTypeID[typeID].append(route)

        return routesByTypeID

    def OnProductEntryClicked(self, entry):
        node = entry.sr.node
        if node.Get('routeID', None) is None:
            self.createRouteButton.state = uiconst.UI_NORMAL
            self.deleteRouteButton.state = uiconst.UI_HIDDEN
        else:
            self.createRouteButton.state = uiconst.UI_HIDDEN
            self.deleteRouteButton.state = uiconst.UI_NORMAL

    def OnProductEntryDblClicked(self, entry):
        node = entry.sr.node
        if node.Get('routeID', None) is None:
            self._CreateRoute('productScroll')

    def _CreateRoute(self, scroll):
        selected = getattr(self, scroll).GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            self.ShowPanel(planetCommonUI.PANEL_CREATEROUTE, entry.typeID, entry.amount)

    def SubmitRoute(self, *args):
        if not getattr(self, 'routeAmountEdit', None):
            return
        sm.GetService('planetUI').myPinManager.CreateRoute(self.routeAmountEdit.GetValue())
        self.HideCurrentPanel()
        self.commodityToRoute = None

    def _DeleteRoute(self):
        selected = self.productScroll.GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            if entry.routeID:
                self.planetUISvc.myPinManager.RemoveRoute(entry.routeID)
                self.LoadProductScroll()
                self.createRouteButton.state = uiconst.UI_HIDDEN
                self.deleteRouteButton.state = uiconst.UI_HIDDEN

    def _DeleteRouteFromEntry(self):
        if not hasattr(self, 'routeScroll'):
            return
        selected = self.routeScroll.GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            if entry.routeID:
                self.planetUISvc.myPinManager.RemoveRoute(entry.routeID)
                self.LoadRouteScroll()
                animations.FadeOut(self.routeInfo, duration=0.125, sleep=True)

    def _CreateTransfer(self, *args):
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            raise UserError('CannotTransferInEditMode')
        self.planetUISvc.myPinManager.EnterRouteMode(self.pin.id, None, oneoff=True)
        self.ShowPanel(planetCommonUI.PANEL_TRANSFER)

    def PanelDecommissionPin(self):
        typeName = evetypes.GetName(self.pin.typeID)
        if evetypes.GetGroupID(self.pin.typeID) == invconst.groupCommandPins:
            text = localization.GetByLabel('UI/PI/Common/DecommissionCommandPin', typeName=typeName)
        else:
            text = localization.GetByLabel('UI/PI/Common/DecommissionLink', typeName=typeName)
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        Label(parent=cont, text=text, align=uiconst.TOTOP)
        btns = [[localization.GetByLabel('UI/PI/Common/Proceed'), self._DecommissionSelf, None]]
        ButtonGroup(btns=btns, idx=0, parent=cont)
        return cont

    def _DecommissionSelf(self, *args):
        sm.GetService('audio').SendUIEvent('msg_pi_build_decommission_play')
        self.planetUISvc.myPinManager.RemovePin(self.pin.id)

    def OnRouteEntryHover(self, entry):
        self.planetUISvc.myPinManager.ShowRoute(entry.sr.node.routeID)

    def OnRouteEntryExit(self, entry):
        self.planetUISvc.myPinManager.StopShowingRoute(entry.sr.node.routeID)

    def OnRefreshPins(self, pinIDs):
        if self.panelID == planetCommonUI.PANEL_STORAGE:
            self.LoadStorageContentScroll()

    def GetPanelID(self):
        return self.panelID

    def ProcessColonyDataSet(self, planetID):
        if self.planetUISvc.planetID != planetID:
            return
        self.pin = sm.GetService('planetSvc').GetPlanet(planetID).GetPin(self.pin.id)

    def PanelShowStats(self, *args):
        cont = Container(parent=self.actionCont, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.statsScroll = scroll = Scroll(parent=cont, name='StatsScroll')
        scrolllist = self.GetStatsEntries()
        scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/PI/Common/Attribute'), localization.GetByLabel('UI/Common/Value')])
        return cont

    def GetStatsEntries(self):
        scrolllist = []
        if self.pin.GetCpuUsage() > 0:
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'), localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=self.pin.GetCpuUsage()))}))
        if self.pin.GetCpuOutput() > 0:
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuOutput'), localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=self.pin.GetCpuOutput()))}))
        if self.pin.GetPowerUsage() > 0:
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'), localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=self.pin.GetPowerUsage()))}))
        if self.pin.GetPowerOutput() > 0:
            scrolllist.append(GetFromClass(Generic, {'label': '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerOutput'), localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=self.pin.GetPowerOutput()))}))
        return scrolllist

    def OnPlanetRouteWaypointAdded(self, currentRoute):
        self.currentRoute = currentRoute
        self.UpdatePanelCreateRoute()

    def PanelCreateRoute(self, typeID, amount):
        self.planetUISvc.myPinManager.EnterRouteMode(self.pin.id, typeID)
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        cont._OnClose = self.OnPanelCreateRouteClosed
        w = self.width - 5
        self.sourceMaxAmount = amount
        self.routeMaxAmount = amount
        self.commodityToRoute = typeID
        self.commoditySourceMaxAmount = amount
        self.currRouteCycleTime = self.pin.GetCycleTime()
        resourceTxt = localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=evetypes.GetName(typeID), amount=int(self.routeMaxAmount))
        CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/CommodityToRoute'), subtext=resourceTxt, iconTypeID=typeID, align=uiconst.TOTOP)
        CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/QtyAmount'), align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padBottom=0)
        amountCont = Container(name='amountCont', parent=cont, align=uiconst.TOTOP, height=HEIGHT_COMPACT, padBottom=4)
        self.routeAmountEdit = SingleLineEditInteger(name='routeAmountEdit', parent=amountCont, setvalue=self.routeMaxAmount, width=100, align=uiconst.TOPLEFT, maxValue=self.routeMaxAmount, OnChange=self.OnRouteAmountEditChanged, density=Density.COMPACT)
        self.routeAmountText = EveLabelSmall(parent=amountCont, left=108, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        self.routeDestText = CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/Common/Destination'), align=uiconst.TOTOP)
        btnGroup = ButtonGroup(parent=cont, line=False, idx=0)
        self.createRouteButton = btnGroup.AddButton(localization.GetByLabel('UI/PI/Common/CreateRoute'), self.SubmitRoute)
        self.UpdatePanelCreateRoute()
        return cont

    def OnPanelCreateRouteClosed(self, *args):
        if not self.destroyed:
            sm.GetService('planetUI').eventManager.SetStateNormal()

    def OnRouteAmountEditChanged(self, newVal):
        try:
            routeAmount = int(newVal)
        except ValueError:
            return

        if not self.currRouteCycleTime:
            return
        routeAmount = min(routeAmount, self.routeMaxAmount)
        routeAmount = max(routeAmount, 0.0)
        volume = planetCommon.GetCommodityTotalVolume({self.commodityToRoute: routeAmount})
        volumePerHour = planetCommon.GetBandwidth(volume, self.currRouteCycleTime)
        sm.GetService('planetUI').myPinManager.OnRouteVolumeChanged(volumePerHour)

    def UpdatePanelCreateRoute(self):
        if not self.currentRoute or len(self.currentRoute) < 2:
            destName = localization.GetByLabel('UI/PI/Common/NoDestinationSelected')
            self.routeMaxAmount = self.sourceMaxAmount
            self.currRouteCycleTime = self.pin.GetCycleTime()
            self.createRouteButton.Disable()
            self.createRouteButton.hint = localization.GetByLabel('UI/PI/Common/NoDestinationSelected')
        else:
            self.routeDestPin = sm.GetService('planetUI').GetCurrentPlanet().GetColony(session.charid).GetPin(self.currentRoute[-1])
            isValid, invalidTxt, self.currRouteCycleTime = planetCommon.GetRouteValidationInfo(self.pin, self.routeDestPin, self.commodityToRoute)
            destName = planetCommon.GetGenericPinName(self.routeDestPin.typeID, self.routeDestPin.id)
            if not isValid:
                destName = localization.GetByLabel('UI/PI/Common/InvalidDestination', destName=destName, reason=invalidTxt)
            if not isValid:
                self.routeMaxAmount = 0
            elif self.routeDestPin.IsProcessor() and self.commodityToRoute in self.routeDestPin.GetConsumables():
                destMaxAmount = self.routeDestPin.GetConsumables().get(self.commodityToRoute)
                if self.pin.IsStorage():
                    self.routeMaxAmount = destMaxAmount
                else:
                    self.routeMaxAmount = min(destMaxAmount, self.commoditySourceMaxAmount)
            else:
                self.routeMaxAmount = self.commoditySourceMaxAmount
            if isValid:
                self.createRouteButton.Enable()
                self.createRouteButton.hint = ''
            else:
                self.createRouteButton.Disable()
                self.createRouteButton.hint = localization.GetByLabel('UI/PI/Common/NoDestinationSelected')
        self.routeAmountEdit.SetText(self.routeMaxAmount)
        self.routeAmountEdit.SetMaxValue(self.routeMaxAmount)
        self.routeAmountText.text = localization.GetByLabel('UI/PI/Common/RoutedPortion', maxAmount=self.routeMaxAmount)
        self.OnRouteAmountEditChanged(self.routeMaxAmount)
        self.routeDestText.SetSubtext(destName)

    def PanelSelectTransferDest(self, *args):
        cont = Container(parent=self.actionCont, pos=(0, 0, 0, 15), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        cont._OnClose = self.OnPanelSelectTransferDestClosed
        Label(parent=cont, text=localization.GetByLabel('UI/PI/Common/SelectTransferDestination'), align=uiconst.TOTOP)
        return cont

    def OnPanelSelectTransferDestClosed(self, *args):
        sm.GetService('planetUI').eventManager.SetStateNormal()

    def SetPin(self, pin):
        self.pin = pin

    def PanelShowRoutes(self, *args):
        self.showRoutesCont = cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.routeScroll = Scroll(parent=cont, name='routeScroll')
        self.routeScroll.multiSelect = False
        self.routeScroll.sr.id = 'planetBaseShowRoutesScroll'
        self.routeInfo = ContainerAutoSize(parent=cont, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, idx=0, padTop=4)
        content_width, _ = self.content.GetAbsoluteSize()
        w = content_width / 2 - 10
        info_cont = ContainerAutoSize(parent=self.routeInfo, align=uiconst.TOTOP)
        self.routeInfoSource = CaptionAndSubtext(parent=info_cont, caption=localization.GetByLabel('UI/PI/Common/Origin'), width=w)
        self.routeInfoDest = CaptionAndSubtext(parent=info_cont, caption=localization.GetByLabel('UI/PI/Common/Destination'), width=w, top=42)
        self.routeInfoType = CaptionAndSubtext(parent=info_cont, caption=localization.GetByLabel('UI/Common/Commodity'), width=w, left=w)
        self.routeInfoBandwidth = CaptionAndSubtext(parent=info_cont, caption=localization.GetByLabel('UI/PI/Common/CapacityUsed'), width=w, left=w, top=42)
        self.routeInfoBtns = ButtonGroup(parent=self.routeInfo, align=uiconst.TOTOP, top=16)
        if self.pin.IsStorage() and hasattr(self, '_CreateRoute'):
            self.createRouteBtn = Button(parent=self.routeInfoBtns, label=localization.GetByLabel('UI/PI/Common/CreateRoute'), func=self._CreateRoute, args='routeScroll')
        Button(parent=self.routeInfoBtns, label=localization.GetByLabel('UI/PI/Common/DeleteRoute'), func=self._DeleteRouteFromEntry, args=())
        self.LoadRouteScroll()
        return cont

    def GetRouteTypeLabel(self, route, pin):
        if not route or not pin:
            return localization.GetByLabel('UI/Common/Unknown')
        elif route.GetSourcePinID() == pin.id:
            return localization.GetByLabel('UI/PI/Common/Outgoing')
        elif route.GetDestinationPinID() == pin.id:
            return localization.GetByLabel('UI/PI/Common/Incoming')
        else:
            return localization.GetByLabel('UI/PI/Common/Transiting')

    def IsTransit(self, route, pin):
        if not route or not pin:
            return False
        if route.GetSourcePinID() == pin.id or route.GetDestinationPinID() == pin.id:
            return False
        return True

    def LoadRouteScroll(self):
        scrolllist = []
        routesShown = []
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Unable to load route scroll without active colony on planet')
        planetUISvc = sm.GetService('planetUI')
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            for routeID in link.routesTransiting:
                if routeID in routesShown:
                    continue
                route = colony.GetRoute(routeID)
                typeID = route.GetType()
                qty = route.GetQuantity()
                typeName = evetypes.GetName(typeID)
                if route.GetSourcePinID() == self.pin.id:
                    sourceText = localization.GetByLabel('UI/PI/Common/ThisStructure')
                else:
                    sourcePin = planetUISvc.planet.GetPin(route.GetSourcePinID())
                    sourceText = GetPinNameShort(sourcePin.typeID, sourcePin.id)
                if route.GetDestinationPinID() == self.pin.id:
                    destText = localization.GetByLabel('UI/PI/Common/ThisStructure')
                else:
                    destPin = planetUISvc.planet.GetPin(route.GetDestinationPinID())
                    destText = GetPinNameShort(destPin.typeID, destPin.id)
                if self.IsTransit(route, self.pin):
                    textColor = '<font color=%s>' % TextColor.SECONDARY.hex_argb
                else:
                    textColor = ''
                scrolllist.append(GetFromClass(Item, {'label': '<t>%s%s<t>%s<t>%s<t>%s<t>%s' % (textColor,
                           typeName,
                           qty,
                           self.GetRouteTypeLabel(route, self.pin),
                           sourceText,
                           destText),
                 'typeID': typeID,
                 'itemID': None,
                 'getIcon': True,
                 'OnMouseEnter': self.OnRouteEntryHover,
                 'OnMouseExit': self.OnRouteEntryExit,
                 'routeID': route.routeID,
                 'OnClick': self.OnRouteEntryClick,
                 'amount': qty}))
                routesShown.append(route.routeID)

        self.routeScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoIncomingOrOutgoingRoutes'), headers=['',
         localization.GetByLabel('UI/Common/Commodity'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/PI/Common/Type'),
         localization.GetByLabel('UI/PI/Common/Origin'),
         localization.GetByLabel('UI/PI/Common/Destination')])

    def OnRouteEntryClick(self, *args):
        selectedRoutes = self.routeScroll.GetSelected()
        if len(selectedRoutes) < 1:
            self.routeInfo.state = uiconst.UI_HIDDEN
            return
        selectedRouteData = selectedRoutes[0]
        selectedRoute = None
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(session.charid)
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            for routeID in link.routesTransiting:
                if routeID == selectedRouteData.routeID:
                    selectedRoute = route = colony.GetRoute(routeID)
                    break

        if selectedRoute is None or not evetypes.Exists(selectedRoute.GetType()):
            return
        if selectedRoute.GetSourcePinID() == self.pin.id:
            self.routeInfoSource.SetSubtext(localization.GetByLabel('UI/PI/Common/ThisStructure'))
        else:
            sourcePin = sm.GetService('planetUI').planet.GetPin(selectedRoute.GetSourcePinID())
            self.routeInfoSource.SetSubtext(planetCommon.GetGenericPinName(sourcePin.typeID, sourcePin.id))
        if selectedRoute.GetDestinationPinID() == self.pin.id:
            self.routeInfoDest.SetSubtext(localization.GetByLabel('UI/PI/Common/ThisStructure'))
        else:
            destPin = sm.GetService('planetUI').planet.GetPin(selectedRoute.GetDestinationPinID())
            self.routeInfoDest.SetSubtext(planetCommon.GetGenericPinName(destPin.typeID, destPin.id))
        routeTypeID = route.GetType()
        routeQty = route.GetQuantity()
        self.routeInfoType.SetSubtext(localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=evetypes.GetName(routeTypeID), amount=int(routeQty)))
        bandwidthAttr = dogma.data.get_attribute(dogma.const.attributeLogisticalCapacity)
        self.routeInfoBandwidth.SetSubtext(GetFormatAndValue(bandwidthAttr, selectedRoute.GetBandwidthUsage()))
        if self.createRouteBtn:
            if selectedRoute.GetDestinationPinID() == self.pin.id:
                self.createRouteBtn.state = uiconst.UI_NORMAL
            else:
                self.createRouteBtn.state = uiconst.UI_HIDDEN
        self.routeInfo.opacity = 0.0
        self.routeInfo.state = uiconst.UI_PICKCHILDREN
        animations.FadeIn(self.routeInfo, duration=0.125, sleep=True)


class IconButton(Container):
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_size = 32
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        size = attributes.get('size', self.default_size)
        color = attributes.get('color', self.default_color)
        self.isSelected = attributes.get('isSelected', False)
        self.icon = Icon(icon=attributes.icon, typeID=attributes.typeID, parent=self, pos=(0,
         0,
         size,
         size), state=uiconst.UI_DISABLED, size=size, ignoreSize=True, color=color)
        self.selectedFrame = Frame(parent=self, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_HIDDEN)
        self.frame = Frame(parent=self, color=(1.0, 1.0, 1.0, 0.8), state=uiconst.UI_HIDDEN)
        if self.isSelected:
            self.SetSelected(True)

    def OnMouseEnter(self, *args):
        self.ShowFrame()

    def OnMouseExit(self, *args):
        if not self.isSelected:
            self.HideFrame()

    def SetSelected(self):
        self.isSelected = True
        self.ShowFrame()

    def SetDeselected(self):
        self.isSelected = False
        self.HideFrame()

    def ShowFrame(self):
        self.frame.state = uiconst.UI_DISABLED
        self.opacity = 1.0

    def HideFrame(self):
        self.frame.state = uiconst.UI_HIDDEN
        self.opacity = 0.3


class CaptionAndSubtext(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_name = 'CaptionAndSubtext'
    default_align = uiconst.TOPLEFT
    default_alignMode = uiconst.TOTOP
    default_width = 180
    default_padBottom = 4

    def ApplyAttributes(self, attributes):
        super(CaptionAndSubtext, self).ApplyAttributes(attributes)
        self.captionTxt = attributes.Get('caption', '')
        self.subtextTxt = attributes.Get('subtext', '')
        self.iconTypeID = attributes.Get('iconTypeID', None)
        self.height = attributes.Get('height', self.default_height)
        self.width = attributes.Get('width', self.default_width)
        self.iconSize = 28
        self.icon = None
        self.CreateLayout()

    def CreateLayout(self):
        if self.iconTypeID:
            padLeft = self.iconSize
        else:
            padLeft = 0
        self.caption = CaptionLabel(parent=self, text=self.captionTxt, padding=(padLeft,
         0,
         4,
         0), align=uiconst.TOTOP)
        self.subtext = EveLabelSmall(parent=self, text=self.subtextTxt, align=uiconst.TOTOP, padding=(padLeft,
         0,
         4,
         0), lineSpacing=-0.1)
        if self.iconTypeID:
            self.icon = Icon(parent=self, pos=(-5,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED, typeID=self.iconTypeID, size=self.iconSize, ignoreSize=True)

    def SetSubtext(self, subtext):
        self.subtextTxt = subtext
        self.subtext.text = self.subtextTxt

    def SetCaption(self, caption):
        self.captionTxt = caption
        self.caption.text = self.captionTxt

    def SetIcon(self, typeID):
        if typeID == self.iconTypeID:
            return
        self.iconTypeID = typeID
        self.Flush()
        self.CreateLayout()

    def GetMenu(self):
        if self.iconTypeID:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(None, self.iconTypeID, includeMarketDetails=True)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.iconTypeID:
            planetCommonUI.LoadProductTooltipPanel(tooltipPanel, self.iconTypeID)


class CaptionLabel(EveLabelSmall):
    default_state = uiconst.UI_DISABLED
    default_color = (1.0, 1.0, 1.0, 0.95)
