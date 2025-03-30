#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\contractsearch.py
import copy
import sys
import evetypes
from carbonui.control.combo import Combo
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import UserSettingBool
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.collapseLine import CollapseLine
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.contracts.contractentry import ContractEntrySearchAuction, ContractEntrySearchCourier, ContractEntrySearchItemExchange
from eve.client.script.ui.util import uix, utilWindows
import uthread
import blue
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.util import searchUtil
from eve.client.script.util.contractutils import GetContractTitle, SelectItemTypeDlg
from eve.common.lib import appConst
from eve.common.script.search import const as search_const
from eve.common.script.sys import idCheckers
from eve.common.script.util import contractscommon as cc
import localization
CONTRACT_SCROLL_COLUMN_WIDTHS = {localization.GetByLabel('UI/Contracts/ContractsSearch/columPickup'): 120,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'): 200,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnBids'): 20,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'): 90,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnRoute'): 80,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'): 60,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'): 70,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnPrice'): 100,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'): 100,
 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'): 100}
CONTRACT_TYPE_OPTIONS = [(localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None),
 (localization.GetByLabel('UI/Contracts/ContractsSearch/comboSellContracts'), 2),
 (localization.GetByLabel('UI/Contracts/ContractsSearch/comboWantToBuy'), 3),
 (localization.GetByLabel('UI/Contracts/ContractsSearch/combo'), 1),
 (localization.GetByLabel('UI/Contracts/ContractsSearch/comboExcluedWantToBuy'), 4)]
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from carbonui.uicore import uicore
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.client.script.ui.util import searchOld
from eveexceptions import UserError
from eveprefs import prefs
from menu import MenuLabel
import metaGroups
LEFT_WIDTH = 170
MILLION = 1000000
MAXJUMPROUTENUM = 100
PAGINGRANGE = 10
NUM_SAVED_LOCATIONS = 5
MAX_NUM_MILLIONS = 100000
CONTRACT_SEARCH_MAPPINGS = {cc.SORT_ID: 'UI/Contracts/ContractsSearch/columnCreated',
 cc.SORT_EXPIRED: 'UI/Contracts/ContractsSearch/columnTimeLeft',
 cc.SORT_PRICE: 'UI/Contracts/ContractsSearch/columnPrice',
 cc.SORT_REWARD: 'UI/Contracts/ContractsSearch/columnReward',
 cc.SORT_COLLATERAL: 'UI/Contracts/ContractsSearch/columnCollateral'}
EDIT_WIDTH = 61

class ContractSearchPanel(Container):

    def ApplyAttributes(self, attributes):
        super(ContractSearchPanel, self).ApplyAttributes(attributes)
        parentContentPadding = attributes.get('parentContentPadding', 16)
        self.contractsSvc = sm.GetService('contracts')
        self.inited = False
        self.searchThread = None
        self.currPage = 0
        self.numPages = 0
        self.pageData = {}
        self.pages = {0: None}
        self.fetchingContracts = 0
        self.fltIssuerID = None
        self.ConstructLeftCont(parentContentPadding)
        self.topContainer = Container(name='topCont', parent=self, pos=(0, 0, 0, 32), align=uiconst.TOTOP)
        self.ConstructViewModeButtons()
        self.ConstructSortCombo()
        self.ConstructBottomFilterCont(parentContentPadding)
        self.ConstructContractsScroll()
        self.ReconstructLeftFilters()
        self.inited = True

    def ConstructLeftCont(self, parentContentPadding):
        resizeCont = DragResizeCont(name='resizeCont', parent=self, align=uiconst.TOLEFT, minSize=180, maxSize=280, defaultSize=200, settingsID='contractSearch_resizer')
        leftPanelPadding = 8
        self.leftCont = Container(name='leftCont', parent=resizeCont, align=uiconst.TOALL, padding=(0,
         0,
         leftPanelPadding,
         0))
        self.ConstructBuySellOrCourierToggleButtons()
        self.searchBtn = Button(name='searchBtn', align=uiconst.TOBOTTOM, parent=self.leftCont, padTop=4, func=self.DoSearch, label=localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch'))
        self.leftFilterScroll = ScrollContainer(name='leftFilterScroll', parent=self.leftCont, align=uiconst.TOALL)
        if isinstance(parentContentPadding, tuple):
            fillPadding = [ -x for x in parentContentPadding ]
        else:
            fillPadding = 4 * [-parentContentPadding]
        fillPadding[2] = 4
        fillPadding = tuple(fillPadding)
        Fill(bgParent=resizeCont, padding=fillPadding, color=(1.0, 1.0, 1.0), opacity=0.05)

    def ConstructViewModeButtons(self):
        currentViewMode = int(prefs.GetValue('contractsSimpleView', 0) or 0)
        self.viewModeDetailsButton = ButtonIcon(parent=self.topContainer, align=uiconst.TOPLEFT, pos=(6, 10, 16, 16), texturePath='res:/UI/Texture/Icons/38_16_157.png', hint=localization.GetByLabel('UI/Common/Details'), func=self.ChangeViewModeDetails)
        if currentViewMode == 0:
            self.viewModeDetailsButton.SetSelected()
        self.viewModeListButton = ButtonIcon(parent=self.topContainer, align=uiconst.TOPLEFT, pos=(22, 10, 16, 16), texturePath='res:/UI/Texture/Icons/38_16_158.png', hint=localization.GetByLabel('UI/Inventory/List'), func=self.ChangeViewModeList, isActive=currentViewMode == 1)
        if currentViewMode == 1:
            self.viewModeListButton.SetSelected()

    def ConstructSortCombo(self):
        self.sortCombo = Combo(name='sort', label=localization.GetByLabel('UI/Contracts/ContractsSearch/SortPageBy'), width=160, parent=self.topContainer, align=uiconst.TOPRIGHT, callback=self.ComboChange)
        self.PopulateSortCombo()

    def ConstructBottomFilterCont(self, parentContentPadding):
        if settings.user.ui.Get('contracts_search_expander_clientFilterExpander', 0):
            filterState = uiconst.UI_PICKCHILDREN
        else:
            filterState = uiconst.UI_HIDDEN
        self.bottomFilterCont = Container(name='bottomFilterCont', parent=self, align=uiconst.TOBOTTOM, state=filterState, clipChildren=True)
        bottomFilterExpanderCont = Container(name='bottomFilterExpanderCont', parent=self, pos=(0, 0, 0, 20), align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, padTop=0, padBottom=4)
        self.collapseLine = CollapseLine(parent=self, collapsingSectionWidth=30, align=uiconst.TOBOTTOM, collapsingSection=self.bottomFilterCont, useCustomTransition=True, settingKey='contracts_search_expander_clientFilterExpander')
        self.collapseLine.on_section_expand.connect(self.ToggleClientFilters)
        self.collapseLine.on_section_collapse.connect(self.ToggleClientFilters)
        hint = self.GetClientFilterText()
        self.collapseLine.SetHint(hint)
        padRight = parentContentPadding[3] if isinstance(parentContentPadding, tuple) else parentContentPadding
        Line(parent=self, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.15), top=-self.collapseLine.height / 2, padRight=-padRight)
        self.pageArea = Container(name='pageArea', parent=bottomFilterExpanderCont, pos=(10,
         0,
         25 * PAGINGRANGE + 40,
         0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        expanderTextContParent = Container(name='expanderTextContParent', parent=bottomFilterExpanderCont, pos=(0, 0, 0, 20), align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        foundLabelText = localization.GetByLabel('UI/Contracts/ContractsSearch/NoSearch')
        self.foundLabel = eveLabel.EveLabelSmall(text=foundLabelText, parent=expanderTextContParent, align=uiconst.CENTERLEFT, left=4, autoFadeSides=16, state=uiconst.UI_NORMAL)
        self.foundLabel.OnClick = self.ToggleClientFiltersOnLabelClick
        fwdCont = Container(name='fwdCont', parent=self.pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.pageFwdBtn = ButtonIcon(name='pageFwdBtn', parent=fwdCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, width=20, height=20, texturePath='res:/UI/Texture/Icons/38_16_224.png', func=self.DoPageNext)
        self.pagingCont = Container(name='pagingCont', parent=self.pageArea, pos=(0,
         0,
         25 * PAGINGRANGE,
         0), align=uiconst.TORIGHT)
        backCont = Container(name='backCont', parent=self.pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.pageBackBtn = ButtonIcon(name='pageBackBtn', parent=backCont, align=uiconst.CENTERLEFT, state=uiconst.UI_HIDDEN, width=20, height=20, texturePath='res:/UI/Texture/Icons/38_16_223.png', func=self.DoPagePrev)

    def ConstructContractsScroll(self):
        self.contractsScroll = eveScroll.Scroll(parent=self, name='contractsScroll', padding=(0, 8, 0, 0))
        self.contractsScroll.sr.id = 'contractlist'
        self.contractsScroll.multiSelect = 0
        self.contractsScroll.ShowHint(localization.GetByLabel('UI/Contracts/ContractsSearch/ClickSearchHint'))
        self.contractsScroll.sr.defaultColumnWidth = CONTRACT_SCROLL_COLUMN_WIDTHS
        self.loadingWheel = LoadingWheel(parent=self.contractsScroll, align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.loadingWheel.Hide()

    def GetTypesFromName(self, itemTypeName, categoryID, groupID):
        itemTypes = searchUtil.GetResultsList(itemTypeName, [search_const.ResultType.item_type])
        retDict = {}
        for x in itemTypes or []:
            if not evetypes.IsPublished(x):
                continue
            if groupID and evetypes.GetGroupID(x) != groupID:
                continue
            if categoryID and evetypes.GetCategoryID(x) != categoryID:
                continue
            retDict[x] = evetypes.GetName(x)

        return retDict

    def ChangeViewModeList(self):
        prefs.SetValue('contractsSimpleView', 1)
        blue.pyos.synchro.Yield()
        self.viewModeListButton.SetSelected()
        self.viewModeDetailsButton.SetDeselected()
        if self.currPage in self.pageData:
            self.RenderPage()

    def ChangeViewModeDetails(self):
        prefs.SetValue('contractsSimpleView', 0)
        blue.pyos.synchro.Yield()
        self.viewModeListButton.SetDeselected()
        self.viewModeDetailsButton.SetSelected()
        if self.currPage in self.pageData:
            self.RenderPage()

    def PopulateSortCombo(self):
        contractType = self.GetContractTypeSetting()
        oldestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/OldestFirst')
        newestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/NewestFirst')
        shortestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/ShortestFirst')
        longestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/LongestFirst')
        lowFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/LowerstFirst')
        highFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/HighestFirst')
        opt = [(localization.GetByLabel('UI/Contracts/ContractsSearch/DateCreatedOption', text=oldestFirst), (cc.SORT_ID, 0)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/DateCreatedOption', text=newestFirst), (cc.SORT_ID, 1)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/TimeLeftOption', text=shortestFirst), (cc.SORT_EXPIRED, 0)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/TimeLeftOption', text=longestFirst), (cc.SORT_EXPIRED, 1))]
        if contractType == const.conTypeCourier:
            opt.extend([(localization.GetByLabel('UI/Contracts/ContractsSearch/RewardOption', text=lowFirst), (cc.SORT_REWARD, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/RewardOption', text=highFirst), (cc.SORT_REWARD, 1)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/CollateralOption', text=lowFirst), (cc.SORT_COLLATERAL, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/CollateralOption', text=highFirst), (cc.SORT_COLLATERAL, 1)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/VolumnOptions', text=lowFirst), (cc.SORT_VOLUME, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/VolumnOptions', text=highFirst), (cc.SORT_VOLUME, 1))])
        else:
            opt.extend([(localization.GetByLabel('UI/Contracts/ContractsSearch/PriceOption', text=lowFirst), (cc.SORT_PRICE, 0)), (localization.GetByLabel('UI/Contracts/ContractsSearch/PriceOption', text=highFirst), (cc.SORT_PRICE, 1))])
        sel = settings.user.ui.Get('contracts_search_sort_%s' % contractType, (cc.SORT_PRICE, 0) if contractType == cc.CONTYPE_AUCTIONANDITEMECHANGE else None)
        self.sortCombo.LoadOptions(opt, sel)

    def GetContractTypeSetting(self):
        return settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)

    def GetContractFiltersMenu(self, *args):
        m = []
        m.append((MenuLabel('UI/Contracts/ContractsSearch/ExcludeUnreacable'), self.ToggleExcludeUnreachable, (None,)))
        m.append((MenuLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), self.ToggleExcludeIgnored, (None,)))
        return m

    def ToggleExcludeUnreachable(self, *args):
        k = 'contracts_search_client_excludeunreachable'
        v = 0 if settings.user.ui.Get(k, 0) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()

    def ToggleExcludeIgnored(self, *args):
        k = 'contracts_search_client_excludeignore'
        v = 0 if settings.user.ui.Get(k, 1) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()

    def ReconstructLeftFilters(self):
        self.leftFilterScroll.Flush()
        contractType = self.GetContractTypeSetting()
        if contractType != const.conTypeCourier:
            self.ConstructTypeNameEdit()
        self.ConstructLocationCombo()
        self.ConstructAdvancedCont()
        if contractType != const.conTypeCourier:
            self.ConstructContractTypeCombo()
            self.ConstructContractCategoryCombo()
            self.ConstructContractGroupCombo()
            self.ConstructBuySellFilterCheckboxes()
            self.ConstructPriceEdits()
            self.fltDropOff = None
        elif contractType == const.conTypeCourier:
            self.ConstructDropOffEdit()
            self.ConstructRewardEdits()
            self.ConstructCollateralEdits()
            self.ConstructVolumeEdits()
        self.ConstructAvailabilityCombo()
        self.ConstrucSecurityCheckboxes()
        self.ConstructIssuerEdit()
        for editName in ['fltMinPrice',
         'fltMaxPrice',
         'fltMinReward',
         'fltMaxReward',
         'fltMinCollateral',
         'fltMaxCollateral',
         'fltMinVolume',
         'fltMaxVolume']:
            edit = getattr(self, editName, None)
            try:
                if not settings.user.ui.Get('contracts_search_%s' % edit.name, ''):
                    edit.SetText('')
                    edit.CheckHintText()
            except:
                sys.exc_clear()

        self.ReconstructBottomFilters(contractType)

    def ReconstructBottomFilters(self, contractType):
        self.bottomFilterCont.Flush()
        grid = LayoutGrid(parent=self.bottomFilterCont, align=uiconst.TOPLEFT, columns=3, left=14, cellSpacing=(8, 2))
        editWidth = 60
        totalHeight = 0
        self.fltClientExcludeNoGateToGateJumps = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeNoGateToGateJumps'), settingsKey='contracts_search_client_excludeunreachable', checked=settings.user.ui.Get('contracts_search_client_excludeunreachable', 1), parent=grid, callback=self.FilterCheckBoxChange, align=uiconst.CENTERLEFT)
        jumpSettings = settings.user.ui.Get('contracts_search_client_maxjumps', 0)
        fltClientMaxJumps = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaximumJumps'), settingsKey='maxjumps', checked=jumpSettings, parent=grid, callback=self.FilterCheckBoxChange, align=uiconst.CENTERLEFT)
        numJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', 10)
        self.maxjumpsInput = SingleLineEditInteger(name='maxjumpsInput', parent=grid, align=uiconst.CENTERLEFT, pos=(0,
         0,
         editWidth,
         10), label='', setvalue=str(numJumps), hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), maxValue=MAXJUMPROUTENUM, OnReturn=self.OnJumpInputReturn, OnFocusLost=self.OnJumpFocusLost)
        if not jumpSettings:
            self.maxjumpsInput.Disable()
        totalHeight += self.maxjumpsInput.height
        self.fltClientExcludeIgnore = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), settingsKey='contracts_search_client_excludeignore', checked=settings.user.ui.Get('contracts_search_client_excludeignore', 1), parent=grid, callback=self.FilterCheckBoxChange, align=uiconst.CENTERLEFT)
        if contractType == const.conTypeCourier:
            routeSettings = settings.user.ui.Get('contracts_search_client_maxroute', 0)
            fltClientMaxRoute = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaxRoute'), settingsKey='maxroute', checked=routeSettings, parent=grid, callback=self.FilterCheckBoxChange, align=uiconst.CENTERLEFT)
            numRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', 10)
            self.maxrouteInput = SingleLineEditInteger(name='maxrouteInput', parent=grid, align=uiconst.CENTERLEFT, pos=(0,
             0,
             editWidth,
             10), label='', setvalue=numRoute, hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), maxValue=MAXJUMPROUTENUM, OnReturn=self.OnRouteInputReturn, OnFocusLost=self.OnRouteFocusLost)
            if not routeSettings:
                self.maxrouteInput.Disable()
            totalHeight += self.maxrouteInput.height
        self.fltClientOnlyCurrentSecurity = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/OnlyCurrentSecurity'), settingsKey='contracts_search_client_currentsecurity', checked=settings.user.ui.Get('contracts_search_client_currentsecurity', 0), parent=grid, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.CENTERLEFT)
        totalHeight += self.fltClientOnlyCurrentSecurity.height
        self.bottomFilterCont.height = totalHeight + 8

    def ConstructIssuerEdit(self):
        issuerID = settings.user.ui.Get('contracts_search_issuer_id', None)
        issuerName = ''
        if issuerID is not None:
            issuerName = cfg.eveowners.Get(issuerID).name
        self.fltIssuer = SingleLineEditText(name='issuer', parent=self.advancedCont, align=uiconst.TOTOP, padTop=8, setvalue=issuerName, hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'), OnReturn=self.ParseIssuers, OnChange=self.OnIssuerChange)
        self.fltIssuer.ShowClearButton(showOnLetterCount=3)
        self.OnIssuerChange(issuerName)
        self.fltIssuerID = issuerID
        self.fltIssuer.OnDropData = self.OnDropIssuer

    def ConstructAvailabilityCombo(self):
        contractAvailability = settings.user.ui.Get('contracts_search_avail', const.conAvailPublic)
        self.fltAvail = Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/Availability'), parent=self.advancedCont, options=self.GetAvailabilityOptions(), name='avail', select=contractAvailability, callback=self.ComboChange, align=uiconst.TOTOP, padTop=24, uniqueUiName=pConst.UNIQUE_NAME_CONTRACT_AVAILABILITY_SETTINGS)

    def ConstrucSecurityCheckboxes(self):
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Contracts/ContractsSearch/SecurityFilters'), parent=self.advancedCont, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=8)
        securityCont = FlowContainer(name='securityCont', parent=self.advancedCont, align=uiconst.TOTOP, contentSpacing=(8, 8))
        self.fltSecHigh = Checkbox(text=localization.GetByLabel('UI/Common/HighSecurityShort'), settingsKey='contracts_search_sechigh', checked=settings.user.ui.Get('contracts_search_sechigh', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/HighSec'), align=uiconst.NOALIGN)
        self.fltSecLow = Checkbox(text=localization.GetByLabel('UI/Common/LowSecurityShort'), settingsKey='contracts_search_seclow', checked=settings.user.ui.Get('contracts_search_seclow', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/LowSec'), align=uiconst.NOALIGN)
        self.fltSecNull = Checkbox(text=localization.GetByLabel('UI/Common/NullSecurityShort'), settingsKey='contracts_search_secnull', checked=settings.user.ui.Get('contracts_search_secnull', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/NullSec'), align=uiconst.NOALIGN)

    def ConstructVolumeEdits(self):
        vars = EditFieldVariables(headerText=localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'), configName='fltVolume', fromConfigName='minvolume', fromMaxValue=None, fromSettingName='contracts_search_minvolume', toConfigName='maxvolume', toMaxValue=None, toSettingName='contracts_search_maxvolume')
        self.fltMinVolume, self.fltMaxVolume, self.fltCbVolume = self.ConstructFromToEditCont(self.advancedCont, vars)

    def ConstructCollateralEdits(self):
        vars = EditFieldVariables(headerText=localization.GetByLabel('UI/Contracts/ContractsSearch/CourierCollateralInMillions'), configName='fltCollateral', fromConfigName='mincollateral', fromMaxValue=MAX_NUM_MILLIONS, fromSettingName='contracts_search_mincollateral', toConfigName='maxcollateral', toMaxValue=MAX_NUM_MILLIONS, toSettingName='contracts_search_maxcollateral')
        self.fltMinCollateral, self.fltMaxCollateral, self.fltCbCollateral = self.ConstructFromToEditCont(self.advancedCont, vars)

    def ConstructRewardEdits(self):
        vars = EditFieldVariables(headerText=localization.GetByLabel('UI/Contracts/ContractsSearch/CourierRewardInMillions'), configName='fltReward', fromConfigName='minreward', fromMaxValue=MAX_NUM_MILLIONS, fromSettingName='contracts_search_minreward', toConfigName='maxreward', toMaxValue=MAX_NUM_MILLIONS, toSettingName='contracts_search_maxreward')
        self.fltMinReward, self.fltMaxReward, self.fltCbReward = self.ConstructFromToEditCont(self.advancedCont, vars)

    def ConstructFromToEditCont(self, parent, editVariables, padTop = 8):
        eveLabel.EveLabelSmall(text=editVariables.headerText, parent=parent, align=uiconst.TOTOP, top=padTop)
        cont = Container(name='cont', parent=parent, align=uiconst.TOTOP)
        innerCont = Container(name='innerCont', parent=cont, align=uiconst.TOALL)
        toEditCont = Container(name='toEditCont', parent=innerCont, align=uiconst.TOLEFT_PROP, width=0.5)
        fromSetValue = settings.user.ui.Get(editVariables.fromSettingName, '')
        fromEdit = SingleLineEditInteger(name=editVariables.fromConfigName, parent=toEditCont, width=EDIT_WIDTH, hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMin'), align=uiconst.TOTOP, maxValue=editVariables.fromMaxValue, setvalue=fromSetValue, OnReturn=self.DoSearch)
        cont.height = fromEdit.height
        toLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Common/ToNumber'), parent=innerCont, align=uiconst.CENTER)
        fromEditCont = Container(name='fromEditCont', parent=innerCont, align=uiconst.TORIGHT_PROP, width=0.5)
        toSetValue = settings.user.ui.Get(editVariables.toSettingName, '')
        toEdit = SingleLineEditInteger(name=editVariables.toConfigName, parent=fromEditCont, label='', hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), align=uiconst.TOTOP, maxValue=editVariables.toMaxValue, setvalue=toSetValue, OnReturn=self.DoSearch)
        toEditCont.padRight = toLabel.width
        fromEditCont.padLeft = toLabel.width

        def SetState(cb):
            if cb.GetValue():
                toEdit.Enable()
                fromEdit.Enable()
                innerCont.Enable()
                toLabel.opacity = 0.75
            else:
                toEdit.Disable()
                fromEdit.Disable()
                innerCont.Disable()
                toLabel.opacity = 0.3

        cbConfigName = 'contracterSearch_%s_cbChecked' % editVariables.configName
        enabled_setting = UserSettingBool(settings_key=cbConfigName, default_value=True)
        filterCb = Checkbox(parent=cont, align=uiconst.CENTERLEFT, callback=SetState, setting=enabled_setting)
        innerCont.padLeft = filterCb.width
        SetState(filterCb)
        return (fromEdit, toEdit, filterCb)

    def ConstructDropOffEdit(self):
        self.fltDropOff = SingleLineEditText(name='dropoff', parent=self.advancedCont, setvalue=settings.user.ui.Get('contracts_search_dropoff', ''), padTop=8, align=uiconst.TOTOP, label='', hintText=localization.GetByLabel('UI/Contracts/ContractsSearch/DropOffLocation'), OnReturn=self.OnDropOffReturn, isLocationField=True)
        self.fltDropOff.ShowClearButton(showOnLetterCount=3)
        self.fltDropOffID = settings.user.ui.Get('contracts_search_dropoff_id', None)

    def GetAvailabilityOptions(self):
        options = [(localization.GetByLabel('UI/Generic/Public'), const.conAvailPublic), (localization.GetByLabel('UI/Contracts/ContractsWindow/Me'), const.conAvailMyself)]
        if not idCheckers.IsNPC(session.corpid):
            options.append((localization.GetByLabel('UI/Generic/MyCorp'), const.conAvailMyCorp))
        if session.allianceid:
            options.append((localization.GetByLabel('UI/Generic/MyAlliance'), const.conAvailMyAlliance))
        return options

    def ConstructPriceEdits(self):
        vars = EditFieldVariables(headerText=localization.GetByLabel('UI/Contracts/ContractsSearch/labelPriceMillions'), configName='fltPrice', fromConfigName='minprice', fromMaxValue=None, fromSettingName='contracts_search_minprice', toConfigName='maxprice', toMaxValue=None, toSettingName='contracts_search_maxprice')
        self.fltMinPrice, self.fltMaxPrice, self.fltCbPrice = self.ConstructFromToEditCont(self.advancedCont, vars)

    def ConstructBuySellFilterCheckboxes(self):
        self.fltExcludeMultiple = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelExcludeMultipleItems'), settingsKey='contracts_search_excludemultiple', checked=settings.user.ui.Get('contracts_search_excludemultiple', 0), parent=self.advancedCont, callback=self.CheckBoxChange, padTop=4, align=uiconst.TOTOP)
        self.fltExactType = Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelExactTypeMatch'), settingsKey='contracts_search_exacttype', checked=settings.user.ui.Get('contracts_search_exacttype', 0), parent=self.advancedCont, callback=self.CheckBoxChange)

    def ConstructContractGroupCombo(self):
        grpOptions = [(localization.GetByLabel('UI/Contracts/ContractsSearch/SelectCategory'), None)]
        self.fltGroups = Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/contractroup'), parent=self.advancedCont, options=grpOptions, name='group', select=settings.user.ui.Get('contracts_search_group', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=24)
        self.PopulateGroupCombo(isSel=True)

    def ConstructContractCategoryCombo(self):
        self.fltCategories = Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/ContractCategory'), parent=self.advancedCont, options=self.GetContractCategoryOptions(), name='category', select=settings.user.ui.Get('contracts_search_category', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=24)

    def GetContractCategoryOptions(self):
        catOptions = [(localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None)]
        categories = []
        principalCategories = [const.categoryBlueprint,
         const.categoryModule,
         const.categoryStructureModule,
         const.categoryShip]
        for categoryID in evetypes.IterateCategories():
            if categoryID > 0 and evetypes.IsCategoryPublishedByCategory(categoryID) and categoryID not in principalCategories:
                categories.append([evetypes.GetCategoryNameByCategory(categoryID), categoryID, 0])

        categories.sort()
        for catID in principalCategories:
            categoryName = evetypes.GetCategoryNameByCategory(catID)
            catOptions.append([categoryName, (catID, 0)])
            if catID == const.categoryBlueprint:
                catOptions.append([localization.GetByLabel('UI/Contracts/ContractsSearch/BlueprintCategoryOriginal', categoryName=categoryName), (catID, cc.SEARCHHINT_BPO)])
                catOptions.append([localization.GetByLabel('UI/Contracts/ContractsSearch/BlueprintCategoryCopy', categoryName=categoryName), (catID, cc.SEARCHHINT_BPC)])

        catOptions.append(['', -1])
        for c in categories:
            catOptions.append((c[0], (c[1], c[2])))

        return catOptions

    def ConstructContractTypeCombo(self):
        self.fltContractOptions = Combo(label=localization.GetByLabel('UI/Contracts/ContractsWindow/ContractType'), parent=self.advancedCont, options=CONTRACT_TYPE_OPTIONS, name='contractOptions', select=settings.user.ui.Get('contracts_search_contractOptions', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=24)

    def ConstructAdvancedCont(self):
        self.advancedCont = ContainerAutoSize(name='advancedCont', parent=self.leftFilterScroll, align=uiconst.TOTOP)
        isExpanded = settings.user.ui.Get('contracts_search_expander_advanced', 0)
        expanderCont = Container(name='advanced', parent=self.leftFilterScroll, height=18, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8, uniqueUiName=pConst.UNIQUE_NAME_SHOW_CONTRACT_OPTIONS)
        expanderCont.onText = localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowLessOptions')
        expanderCont.offText = localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowMoreOptions')
        expanderCont.collapsingCont = self.advancedCont
        expandText = [localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowMoreOptions'), localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowLessOptions')][isExpanded]
        expanderCont.label = eveLabel.EveLabelSmallBold(parent=expanderCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=expandText)
        expanderCont.OnClick = (self.ToggleAdvanced, expanderCont)
        texturePath = 'res:/UI/Texture/classes/Neocom/arrowUp.png' if isExpanded else 'res:/UI/Texture/classes/Neocom/arrowDown.png'
        expanderCont.expander = Sprite(parent=expanderCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, width=7, height=7, texturePath=texturePath)
        self.advancedCont.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][isExpanded]
        self.advancedDivider = expanderCont

    def ConstructLocationCombo(self):
        self.fltLocation = Combo(label=localization.GetByLabel('UI/Common/Location'), parent=self.leftFilterScroll, align=uiconst.TOTOP, padTop=24, options=[], name='location', callback=self.ComboChange)
        self.PopulateLocationCombo()

    def ConstructTypeNameEdit(self):
        self.typeName = SingleLineEditText(name='type', parent=self.leftFilterScroll, label='', hintText=localization.GetByLabel('UI/Wallet/WalletWindow/ItemType'), setvalue=settings.user.ui.Get('contracts_search_typename', ''), align=uiconst.TOTOP, padTop=8, OnReturn=self.DoSearch, isTypeField=True)
        self.typeName.ShowClearButton(showOnLetterCount=3)

    def ConstructBuySellOrCourierToggleButtons(self):
        buttonGroup = ToggleButtonGroup(parent=self.leftCont, align=uiconst.TOTOP, callback=self.OnButtonSelected, padding=(2, 8, 2, 0))
        buttonGroup.AddButton(cc.CONTYPE_AUCTIONANDITEMECHANGE, localization.GetByLabel('UI/Contracts/ContractsSearch/tabBuyAndSell'))
        buttonGroup.AddButton(appConst.conTypeCourier, localization.GetByLabel('UI/Contracts/ContractsSearch/tabCourier'))
        buttonGroup.SelectByID(self.GetContractTypeSetting())

    def SetInitialFocus(self):
        uicore.registry.SetFocus(self.contractsScroll)

    def OnButtonSelected(self, mode, *args):
        if mode == self.GetContractTypeSetting():
            return
        settings.user.ui.Set('contracts_search_type', mode)
        self.PopulateSortCombo()
        uthread.new(self.ReconstructLeftFilters)

    def ComboChange(self, wnd, *args):
        if wnd.name == 'sort':
            contractType = self.GetContractTypeSetting()
            settings.user.ui.Set('contracts_search_sort_%s' % contractType, wnd.GetValue())
        else:
            settings.user.ui.Set('contracts_search_%s' % wnd.name, wnd.GetValue())
        if wnd.name == 'category':
            self.PopulateGroupCombo()
        elif wnd.name == 'type':
            self.ReconstructLeftFilters()
        elif wnd.name == 'location':
            v = wnd.GetValue()
            if v == 10:
                self.PickLocation()
        elif wnd.name == 'sort':
            val = wnd.GetValue()
            sortBy = localization.GetByLabel(CONTRACT_SEARCH_MAPPINGS.get(val[0], 'UI/Contracts/ContractsSearch/columnCreated'))
            pr = settings.user.ui.Get('scrollsortby_%s' % uiconst.SCROLLVERSION, {})
            pr[self.contractsScroll.sr.id] = (sortBy, not not val[1])
            if self.currPage in self.pageData:
                self.DoSearch()

    def PickLocation(self):
        desc = localization.GetByLabel('UI/Contracts/ContractsSearch/labelEnterLocationName')
        ret = utilWindows.NamePopup(localization.GetByLabel('UI/Contracts/ContractsSearch/labelEnterName'), desc, '', maxLength=20)
        if ret:
            name = ret.lower()
            locationID = self.SearchLocation(name)
            if locationID:
                self.DoPickLocation(locationID)

    def DoPickLocation(self, locationID):
        settings.user.ui.Set('contracts_search_location', locationID)
        customLocations = settings.user.ui.Get('contracts_search_customlocations', [])
        loc = (cfg.evelocations.Get(locationID).name, locationID)
        try:
            customLocations.remove(loc)
        except:
            pass

        customLocations.append(loc)
        if len(customLocations) > NUM_SAVED_LOCATIONS:
            del customLocations[0]
        settings.user.ui.Set('contracts_search_customlocations', customLocations)
        self.PopulateLocationCombo()

    def CheckBoxChange(self, wnd, *args):
        pass

    def GetClientFilterText(self):
        contractType = self.GetContractTypeSetting()
        excluded = ''
        for each, text, default in [('excludeunreachable', localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeUnreacable'), 1), ('excludeignore', localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), 1), ('currentsecurity', localization.GetByLabel('UI/Contracts/ContractsSearch/OnlyCurrentSecurity'), 0)]:
            isChecked = settings.user.ui.Get('contracts_search_client_%s' % each, default)
            if isChecked is None:
                continue
            if isChecked:
                excluded += '<br>%s' % text

        isChecked = settings.user.ui.Get('contracts_search_client_maxjumps', None)
        if isChecked:
            maxJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', '-')
            excluded += '<br>%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaximumJumpsDisttance', maxJumps=maxJumps)
        if contractType == const.conTypeCourier:
            isChecked = settings.user.ui.Get('contracts_search_client_maxroute', None)
            if isChecked:
                maxRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', '-')
                excluded += '<br>%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaxRouteDistance', maxRoute=maxRoute)
        hintText = '<b>%s</b>' % localization.GetByLabel('UI/Contracts/ContractsSearch/hintPageFilter')
        if excluded:
            hintText += excluded
        else:
            hintText += '<br>%s' % localization.GetByLabel('UI/Common/Show all')
        return hintText

    def UpdatePaging(self, currentPage, numPages):
        self.pagingCont.Flush()
        if numPages == 1:
            self.pageBackBtn.state = uiconst.UI_HIDDEN
            self.pageFwdBtn.state = uiconst.UI_HIDDEN
            return
        currentRange = (currentPage - 1) / PAGINGRANGE * PAGINGRANGE
        pages = []
        for i in xrange(0, PAGINGRANGE):
            page = currentRange + i
            if page >= numPages:
                break
            pages.append(page)

        for i, pageNum in enumerate(pages):
            PageLink(name='pageNum', parent=self.pagingCont, align=uiconst.TOLEFT, left=0 if i == 0 else 4, label=str(pageNum + 1), onClick=lambda page = pageNum: self.GoToPage(page), selected=pageNum + 1 == currentPage)

        self.pageArea.width = 25 * len(pages) + 40
        backState = uiconst.UI_NORMAL
        if currentPage <= 1:
            backState = uiconst.UI_HIDDEN
        fwdState = uiconst.UI_NORMAL
        if currentPage >= numPages:
            fwdState = uiconst.UI_HIDDEN
        self.pageBackBtn.state = backState
        self.pageFwdBtn.state = fwdState
        self.pagingCont.width = 24 * len(pages) - 4

    def ToggleAdvanced(self, expanderCont, force = None, *args):
        settingsName = 'contracts_search_expander_%s' % expanderCont.name
        if force is None:
            expanded = not settings.user.ui.Get(settingsName, 0)
        else:
            expanded = force
        settings.user.ui.Set(settingsName, expanded)
        if expanded:
            expanderCont.expander.texturePath = 'res:/UI/Texture/classes/Neocom/arrowUp.png'
        else:
            expanderCont.expander.texturePath = 'res:/UI/Texture/classes/Neocom/arrowDown.png'
        expanderCont.label.text = [expanderCont.offText, expanderCont.onText][expanded]
        if expanded:
            expanderCont.collapsingCont.state = uiconst.UI_PICKCHILDREN
        else:
            expanderCont.collapsingCont.state = uiconst.UI_HIDDEN

    def ToggleClientFiltersOnLabelClick(self, *args):
        isExpanded = not self.collapseLine.isCollapsedSetting.get()
        if isExpanded:
            self.collapseLine.SetCollapsed()
        else:
            self.collapseLine.SetExpanded()

    def ToggleClientFilters(self, *args):
        settingsName = 'contracts_search_expander_clientFilterExpander'
        expanded = not settings.user.ui.Get(settingsName, 0)
        settings.user.ui.Set(settingsName, expanded)
        self.UpdateClientFilterHint()

    def UpdateClientFilterHint(self):
        expanded = settings.user.ui.Get('contracts_search_expander_clientFilterExpander', 0)
        if expanded:
            self.bottomFilterCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.bottomFilterCont.state = uiconst.UI_HIDDEN
        hint = self.GetClientFilterText()
        self.collapseLine.SetHint(hint)

    def FilterCheckBoxChange(self, cb, *args):
        if cb.settingsKey in ('maxjumps', 'maxroute'):
            cfgname = 'contracts_search_client_%s' % cb.settingsKey
            cfgnameNum = '%s_num' % cfgname
            inputField = getattr(self, '%sInput' % cb.settingsKey, None)
            if cb.checked:
                inputField.Enable()
                input = inputField.GetValue()
                num = min(input, MAXJUMPROUTENUM)
                inputField.SetValue(str(num))
                settings.user.ui.Set(cfgname, 1)
                settings.user.ui.Set(cfgnameNum, num)
            else:
                inputField.Disable()
                settings.user.ui.Set(cfgname, 0)
        self.UpdateClientFilterHint()
        if self.currPage in self.pageData:
            self.RenderPage()

    def OnJumpInputReturn(self, *args):
        value = min(self.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxjumps_num', value)
        self.UpdateClientFilterHint()
        if self.currPage in self.pageData:
            self.RenderPage()

    def OnJumpFocusLost(self, *args):
        value = min(self.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxjumps_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()

    def OnRouteInputReturn(self, *args):
        value = min(self.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxroute_num', value)
        if self.currPage in self.pageData:
            self.RenderPage()

    def OnRouteFocusLost(self, *args):
        value = min(self.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxroute_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()

    def OnDropOffReturn(self, *args):
        self.ParseDropOff()
        self.DoSearch()

    def OnDropIssuer(self, dragObj, nodes):
        node = nodes[0]
        if node.Get('__guid__', None) not in AllUserEntries():
            return
        charID = node.charID
        if idCheckers.IsCharacter(charID) or idCheckers.IsCorporation(charID):
            issuerName = cfg.eveowners.Get(charID).name
            self.fltIssuer.SetValue(issuerName)
            self.fltIssuerID = charID

    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        typeID = None
        if guid in ('xtriui.InvItem', 'listentry.InvItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem'):
            typeID = getattr(node, 'typeID', None)
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.typeName.SetValue(typeName)
            self.fltExactType.SetChecked(1, 0)

    def PopulateLocationCombo(self):
        self.locationOptions = [(localization.GetByLabel('UI/Generic/CurrentStation'), 0),
         (localization.GetByLabel('UI/Generic/CurrentSystem'), 1),
         (localization.GetByLabel('UI/Generic/CurrentConstellation'), 3),
         (localization.GetByLabel('UI/Corporations/Assets/CurrentRegion'), 2),
         (localization.GetByLabel('UI/Corporations/Assets/AllRegions'), 7),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/PickLocation'), 10)]
        settingsLocationID = settings.user.ui.Get('contracts_search_location', 2)
        customLocations = copy.copy(settings.user.ui.Get('contracts_search_customlocations', []))
        customLocations.reverse()
        if customLocations:
            mrk = ''
            self.locationOptions.append((mrk, None))
            for l in customLocations:
                self.locationOptions.append((l[0], l[1]))

        if settingsLocationID is not None and settingsLocationID > 100:
            try:
                self.locationOptions.insert(0, (cfg.evelocations.Get(settingsLocationID).name, settingsLocationID))
            except:
                pass

        self.fltLocation.LoadOptions(self.locationOptions, settingsLocationID)

    def PopulateGroupCombo(self, isSel = False):
        v = self.fltCategories.GetValue()
        categoryID = v[0] if v and v != -1 else None
        groups = [(localization.GetByLabel('UI/Contracts/ContractsSearch/SelectCategory'), None)]
        if categoryID and evetypes.CategoryExists(categoryID):
            groups = []
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                if evetypes.IsGroupPublishedByGroup(groupID):
                    groups.append((evetypes.GetGroupNameByGroup(groupID), groupID))

            groups.sort(key=lambda x: x[0].lower())
            groups.insert(0, (localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None))
        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_search_group', None)
        self.fltGroups.LoadOptions(groups, sel)
        if categoryID is None:
            self.fltGroups.state = uiconst.UI_HIDDEN
        else:
            self.fltGroups.state = uiconst.UI_NORMAL

    def Load(self, args):
        if not self.inited:
            return

    def Height(self):
        return self.height or self.absoluteBottom - self.absoluteTop

    def Width(self):
        return self.width or self.absoluteRight - self.absoluteLeft

    def ShowLoad(self):
        from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
        ContractsWindow.GetIfOpen().ShowLoad()

    def HideLoad(self):
        from eve.client.script.ui.shared.neocom.contracts.contractsWnd import ContractsWindow
        ContractsWindow.GetIfOpen().HideLoad()

    def DoSearch(self, *args):
        if self.searchBtn.state == uiconst.UI_DISABLED:
            raise UserError('ConPleaseWait')
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.pageData = {}
        self.searchBtn.state = uiconst.UI_DISABLED
        self.searchBtn.SetLabel('<color=gray>' + localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch') + '</color>')
        uthread.new(self.EnableSearchButton)
        self.ShowLoad()
        try:
            self.SearchContracts(reset=True)
        finally:
            self.HideLoad()
            self.IndicateLoading(loading=0)

    def EnableSearchButton(self):
        blue.pyos.synchro.SleepWallclock(2000)
        try:
            self.searchBtn.state = uiconst.UI_NORMAL
            self.searchBtn.SetLabel(localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch'))
        except:
            pass

    def GoToPage(self, pageNum):
        if pageNum < 0:
            return
        if pageNum >= self.numPages:
            return
        self.currPage = pageNum
        self.DoPage(nav=0)

    def DoPagePrev(self, *args):
        self.DoPage(-1)

    def DoPageNext(self, *args):
        self.DoPage(1)

    def DoPage(self, nav = 1, *args):
        p = self.currPage + nav
        if p < 0:
            return
        if p >= self.numPages:
            return
        self.currPage = p
        if self.currPage in self.pageData:
            self.contractsSvc.LogInfo('Page', self.currPage, 'found in cache')
            self.RenderPage()
            return
        self.contractsSvc.LogInfo('Page', self.currPage, 'not found in cache')
        if self.searchThread:
            self.searchThread.kill()
        self.searchThread = uthread.new(self.DoPageThread)

    def DoPageThread(self):
        self.IndicateLoading(loading=1)
        blue.pyos.synchro.SleepWallclock(500)
        self.SearchContracts(page=self.currPage, contractType=self.contractType, availability=self.availability, override=self.override)

    def OnIssuerChange(self, text, *args):
        if self.fltIssuerID is not None:
            self.fltIssuerID = None
            settings.user.ui.Set('contracts_search_issuer_id', None)

    def ClearEditField(self, editField, *args):
        editField.SetValue('')

    def ParseIssuers(self, *args):
        if self.destroyed:
            return
        wnd = self.fltIssuer
        if not wnd or wnd.destroyed:
            return
        name = wnd.GetValue().strip()
        if not name:
            return
        ownerID = searchOld.Search(name.lower(), const.groupCharacter, const.categoryOwner, hideNPC=1, searchWndName='contractIssuerSearch')
        if ownerID:
            self.fltIssuer.SetValue(cfg.eveowners.Get(ownerID).name)
            self.fltIssuerID = ownerID

    def GetLocationGroupID(self, locationID):
        if idCheckers.IsSolarSystem(locationID):
            return const.groupSolarSystem
        if idCheckers.IsConstellation(locationID):
            return const.groupConstellation
        if idCheckers.IsRegion(locationID):
            return const.groupRegion

    def ParseDropOff(self, *args):
        if self.destroyed:
            return
        wnd = self.fltDropOff
        if not wnd or wnd.destroyed:
            return
        name = wnd.GetValue().strip().lower()
        locationID = self.SearchLocation(name)
        if locationID:
            name = cfg.evelocations.Get(locationID).name
            self.fltDropOffID = locationID
            wnd.SetValue(name)

    def SearchLocation(self, name):
        if not name:
            return None
        resultList = searchUtil.GetResultsList(name, search_const.location_result_types)
        foundList = []
        for l in resultList:
            groupID = self.GetLocationGroupID(l)
            if not groupID:
                continue
            groupName = {const.groupSolarSystem: localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
             const.groupConstellation: localization.GetByLabel('UI/Common/LocationTypes/Constellation'),
             const.groupRegion: localization.GetByLabel('UI/Common/LocationTypes/Region')}.get(groupID, '')
            foundList.append((localization.GetByLabel('UI/Contracts/ContractsSearch/FormatSearchLocation', locationID=l, groupName=groupName), l, groupID))

        if not foundList:
            raise UserError('NoLocationFound', {'name': name})
        if len(foundList) == 1:
            chosen = foundList[0]
        else:
            chosen = uix.ListWnd(foundList, '', localization.GetByLabel('UI/Contracts/ContractsSearch/SelectLocation'), localization.GetByLabel('UI/Contracts/ContractsSearch/LocationSearchHint', foundList=len(foundList)), 1, minChoices=1, isModal=1, windowName='locationsearch', unstackable=1)
        if chosen:
            return chosen[1]
        else:
            return None

    def ResetTypeFilters(self):
        self.typeName.SetValue('')
        self.fltExactType.SetChecked(0, 0)
        self.fltCategories.SelectItemByValue(None)
        settings.user.ui.Set('contracts_search_category', None)
        self.PopulateGroupCombo()

    def ResetFields(self, *args):
        fields = ['fltMaxPrice',
         'fltMinPrice',
         'fltMaxVolume',
         'fltMinVolume',
         'fltMaxCollateral',
         'fltMinCollateral',
         'fltMinReward',
         'fltMaxReward']
        for name in fields:
            field = getattr(self, name, None)
            if field is None or field.destroyed:
                continue
            field.SetValue('')
            field.SetText('')
            field.CheckHintText()

        if self.fltDropOff:
            self.fltDropOff.SetValue('')
            self.fltDropOffID = None
        if self.fltIssuer:
            self.fltIssuer.SetValue('')
        self.fltIssuerID = None
        try:
            if self.fltDropOff:
                self.fltDropOff.SetValue('')
                self.fltDropOffID = None
        except:
            pass

    def ResetCheckboxes(self, *args):
        checkboxes = [('fltExcludeTrade', 0),
         ('fltExcludeMultiple', 0),
         ('fltSecNull', 1),
         ('fltSecLow', 1),
         ('fltSecHigh', 1)]
        for name, val in checkboxes:
            cb = getattr(self, name, None)
            if cb is None or cb.destroyed:
                continue
            cb.SetValue(val)

    def FindMyContracts(self, contractType = cc.CONTYPE_AUCTIONANDITEMECHANGE, isCorp = False):
        self.SearchContracts(contractType=contractType, availability=const.conAvailMyCorp if isCorp else const.conAvailMyself, override=True)

    def FindRelated(self, typeID, groupID, categoryID, issuerID, locationID, endLocationID, avail, contractType, reset = True):
        self.ToggleAdvanced(expanderCont=self.advancedDivider, force=1)
        if contractType and self.GetContractTypeSetting() != contractType:
            settings.user.ui.Set('contracts_search_type', contractType)
            self.PopulateSortCombo()
            self.ReconstructLeftFilters()
        if reset:
            if self.fltAvail.GetValue() != avail:
                settings.user.ui.Set('contracts_search_avail', avail)
                self.ReconstructLeftFilters()
            if contractType and contractType != const.conTypeCourier:
                self.ResetTypeFilters()
            self.ResetFields()
            self.fltLocation.SelectItemByValue(7)
        if issuerID:
            issuerName = cfg.eveowners.Get(issuerID).name
            self.fltIssuer.SetValue(issuerName)
            self.fltIssuerID = issuerID
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.typeName.SetValue(typeName)
            self.fltExactType.SetChecked(1, 0)
        elif categoryID:
            self.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
        elif groupID:
            categoryID = evetypes.GetCategoryIDByGroup(groupID)
            self.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
            self.fltGroups.SelectItemByValue(groupID)
        if locationID:
            self.DoPickLocation(locationID)
        if endLocationID:
            locationName = cfg.evelocations.Get(endLocationID).name
            self.fltDropOff.SetValue(locationName)
            self.fltDropOffID = endLocationID
        self.SearchContracts()

    def SearchContracts(self, page = 0, reset = False, contractType = None, availability = None, override = False):
        self.IndicateLoading(loading=1)
        self.currPage = page
        self.override = override
        self.contractType = contractType
        self.availability = availability
        advancedVisible = self.advancedCont.state != uiconst.UI_HIDDEN
        if override:
            itemTypes = None
            itemTypeName = None
            itemCategoryID = None
            itemGroupID = None
            contractType = contractType
            securityClasses = [const.securityClassZeroSec, const.securityClassLowSec, const.securityClassHighSec]
            locationID = None
            endLocationID = None
            issuerID = None
            minPrice = None
            maxPrice = None
            minReward = None
            maxReward = None
            minCollateral = None
            maxCollateral = None
            minVolume = None
            maxVolume = None
            excludeTrade = False
            excludeMultiple = False
            excludeNoBuyout = False
            availability = availability
            searchHint = None
        else:
            issuerID = None
            if advancedVisible:
                if self.fltIssuerID is None and self.fltIssuer.GetValue():
                    self.ParseIssuers()
                if self.fltIssuerID:
                    issuerID = self.fltIssuerID
                    settings.user.ui.Set('contracts_search_issuer_id', issuerID)
            if contractType is None:
                contractType = self.GetContractTypeSetting()
            if availability is None:
                if advancedVisible:
                    availability = self.fltAvail.GetValue()
                else:
                    availability = const.conAvailPublic
            locationID = self.fltLocation.GetValue()
            if locationID < 100:
                if locationID == 0 and not (session.stationid or session.structureid):
                    raise UserError('ConNotInStation')
                locationID = {0: session.stationid or session.structureid,
                 1: session.solarsystemid2,
                 2: session.regionid,
                 3: session.constellationid}.get(locationID, None)
            endLocationID = None
            if advancedVisible and contractType == const.conTypeCourier:
                endLocationName = self.fltDropOff.GetValue()
                if endLocationName and self.fltDropOffID:
                    endLocationID = self.fltDropOffID
                    if endLocationID is None:
                        raise UserError('ConDropOffNotFound', {'name': endLocationName})
                settings.user.ui.Set('contracts_search_dropoff', endLocationName or '')
                settings.user.ui.Set('contracts_search_dropoff_id', endLocationID)
            securityClasses = None
            if advancedVisible:
                secNull = not not self.fltSecNull.checked
                secLow = not not self.fltSecLow.checked
                secHigh = not not self.fltSecHigh.checked
                if False in (secNull, secLow, secHigh):
                    securityClasses = []
                    if secNull:
                        securityClasses.append(const.securityClassZeroSec)
                    if secLow:
                        securityClasses.append(const.securityClassLowSec)
                    if secHigh:
                        securityClasses.append(const.securityClassHighSec)
                    securityClasses = securityClasses or None
            minPrice = None
            maxPrice = None
            if advancedVisible and const.conTypeCourier != contractType:
                if self.fltCbPrice.GetValue():
                    m = self.fltMinPrice.GetValue()
                    settings.user.ui.Set('contracts_search_minprice', m)
                    if m:
                        minPrice = int(m) * MILLION
                    m = self.fltMaxPrice.GetValue()
                    settings.user.ui.Set('contracts_search_maxprice', m)
                    if m:
                        maxPrice = int(m) * MILLION
            minReward = None
            maxReward = None
            minCollateral = None
            maxCollateral = None
            minVolume = None
            maxVolume = None
            if advancedVisible and const.conTypeCourier == contractType:
                if self.fltCbReward.GetValue():
                    m = self.fltMinReward.GetValue()
                    settings.user.ui.Set('contracts_search_minreward', m)
                    if m:
                        minReward = int(m) * MILLION
                    m = self.fltMaxReward.GetValue()
                    settings.user.ui.Set('contracts_search_maxreward', m)
                    if m:
                        maxReward = int(m) * MILLION
                if self.fltCbCollateral.GetValue():
                    m = self.fltMinCollateral.GetValue()
                    settings.user.ui.Set('contracts_search_mincollateral', m)
                    if m:
                        minCollateral = int(m) * MILLION
                    m = self.fltMaxCollateral.GetValue()
                    settings.user.ui.Set('contracts_search_maxcollateral', m)
                    if m:
                        maxCollateral = int(m) * MILLION
                if self.fltCbVolume.GetValue():
                    m = self.fltMinVolume.GetValue()
                    settings.user.ui.Set('contracts_search_minvolume', m)
                    if m:
                        minVolume = int(m)
                    m = self.fltMaxVolume.GetValue()
                    settings.user.ui.Set('contracts_search_maxvolume', m)
                    if m:
                        maxVolume = int(m)
            itemCategoryID = None
            itemGroupID = None
            itemTypes = None
            excludeTrade = None
            excludeMultiple = None
            excludeNoBuyout = None
            itemTypeName = None
            searchHint = None
            if contractType != const.conTypeCourier:
                isExact = False
                if advancedVisible:
                    cv = self.fltCategories.GetValue()
                    if cv and cv != -1:
                        itemCategoryID = int(cv[0])
                        searchHint = int(cv[1])
                    if self.fltGroups.GetValue():
                        itemGroupID = int(self.fltGroups.GetValue())
                    isExact = self.fltExactType.checked
                typeName = self.typeName.GetValue()
                if typeName:
                    metaLevels = []
                    if '|' in typeName:
                        lst = typeName.split('|')
                        typeName = lst[0]
                        metaNames = lst[1].lower()
                        for metaName in metaNames.split(','):
                            groupIDsByName = {'tech i': 1,
                             'tech ii': 2,
                             'tech iii': 14,
                             'storyline': 3,
                             'faction': 4,
                             'officer': 5,
                             'deadspace': 6}
                            vals = groupIDsByName.values()
                            legalGroups = {}
                            for v in vals:
                                legalGroups[metaGroups.get_name(v)] = v

                            groupIDsByName = {k.lower():v for k, v in legalGroups.iteritems()}
                            legalGroups = legalGroups.keys()
                            legalGroups.sort()
                            metaLevel = groupIDsByName.get(metaName, None)
                            if metaName and metaLevel is None:
                                raise UserError('ConMetalevelNotFound', {'level': metaName,
                                 'legal': ', '.join(legalGroups)})
                            metaLevels.append(metaLevel)

                    groupOrCategory = ''
                    if ':' in typeName:
                        lst = typeName.split(':')
                        groupOrCategory = lst[0].lower()
                        found = False
                        for groupID in evetypes.IterateGroups():
                            if evetypes.GetGroupNameByGroup(groupID).lower() == groupOrCategory:
                                itemGroupID = groupID
                                itemCategoryID = evetypes.GetCategoryIDByGroup(groupID)
                                found = True
                                sm.GetService('contracts').LogInfo('Found group:', groupID)
                                break

                        for categoryID in evetypes.IterateCategories():
                            if evetypes.GetCategoryNameByCategory(categoryID).lower() == groupOrCategory:
                                itemGroupID = None
                                itemCategoryID = categoryID
                                found = True
                                sm.GetService('contracts').LogInfo('Found category:', categoryID)
                                break

                        if found:
                            typeName = lst[1]
                        else:
                            sm.GetService('contracts').LogInfo('Did not find group or category matching', groupOrCategory)
                            groupOrCategory = ''
                    itemTypes = self.GetTypesFromName(typeName, itemCategoryID, itemGroupID)
                    if metaLevels:
                        typeIDs = itemTypes.keys()
                        itemTypes = set()
                        for typeID in typeIDs:
                            try:
                                tech = evetypes.GetTechLevel(typeID)
                                meta = evetypes.GetMetaGroupID(typeID)
                                if meta:
                                    if meta in metaLevels:
                                        itemTypes.add(typeID)
                                elif tech in metaLevels:
                                    itemTypes.add(typeID)
                            except:
                                pass

                    else:
                        itemTypes = set(itemTypes.keys())
                    if isExact and itemTypes:
                        if len(itemTypes) > 1:
                            for checkTypeID in itemTypes:
                                if evetypes.GetName(checkTypeID).lower() == typeName.lower():
                                    typeID = checkTypeID
                                    break
                            else:
                                typeID = SelectItemTypeDlg(itemTypes)

                        else:
                            typeID = list(itemTypes)[0]
                        if not typeID:
                            return
                        name = evetypes.GetName(typeID)
                        if groupOrCategory:
                            name = '%s:%s' % (groupOrCategory, name)
                        self.typeName.SetValue(name)
                        itemTypes = {typeID: None}
                if not itemTypes and typeName:
                    raise UserError('ConNoTypeMatchFound', {'name': typeName})
                itemTypeName = self.typeName.GetValue() or None
                settings.user.ui.Set('contracts_search_typename', itemTypeName or '')
                excludeMultiple = self.fltExcludeMultiple.checked
                if contractType != const.conTypeCourier:
                    opt = self.fltContractOptions.GetValue()
                    if opt:
                        if opt == 1:
                            contractType = const.conTypeAuction
                        elif opt == 2:
                            contractType = const.conTypeItemExchange
                            if not minPrice:
                                minPrice = 1
                            excludeTrade = True
                        elif opt == 3:
                            contractType = const.conTypeItemExchange
                            if not maxPrice:
                                maxPrice = 0
                        elif opt == 4:
                            contractType = cc.CONTYPE_AUCTIONANDITEMECHANGE
                            if not minPrice:
                                minPrice = 1
                            excludeTrade = True
        startNum = page * cc.CONTRACTS_PER_PAGE
        sortBy, sortDir = self.sortCombo.GetValue()
        description = None
        ret = sm.ProxySvc('contractProxy').SearchContracts(itemTypes=itemTypes, itemTypeName=itemTypeName, itemCategoryID=itemCategoryID, itemGroupID=itemGroupID, contractType=contractType, securityClasses=securityClasses, locationID=locationID, endLocationID=endLocationID, issuerID=issuerID, minPrice=minPrice, maxPrice=maxPrice, minReward=minReward, maxReward=maxReward, minCollateral=minCollateral, maxCollateral=maxCollateral, minVolume=minVolume, maxVolume=maxVolume, excludeTrade=excludeTrade, excludeMultiple=excludeMultiple, excludeNoBuyout=excludeNoBuyout, availability=availability, description=description, searchHint=searchHint, sortBy=sortBy, sortDir=sortDir, startNum=startNum)
        contracts = ret.contracts
        numFound = ret.numFound
        searchTime = ret.searchTime
        maxResults = ret.maxResults
        self.numPages = int(int(numFound) / cc.CONTRACTS_PER_PAGE)
        if not numFound or self.numPages * cc.CONTRACTS_PER_PAGE < numFound:
            self.numPages += 1
        if numFound >= maxResults:
            numFound = '%s+' % maxResults
        if len(contracts) >= 2:
            self.pages[self.currPage] = contracts[0].contract.contractID
            self.pages[self.currPage + 1] = contracts[-1].contract.contractID - 1
        ownerIDs = set()
        for r in contracts:
            ownerIDs.add(r.contract.issuerID)
            ownerIDs.add(r.contract.issuerCorpID)
            ownerIDs.add(r.contract.assigneeID)

        cfg.eveowners.Prime(ownerIDs)
        self.contractsScroll.sr.id = None
        pathfinderSvc = sm.GetService('clientPathfinderService')
        securitySvc = sm.StartService('securitySvc')
        jumpsCache = {}
        routes = {}
        data = []
        for _c in contracts:
            blue.pyos.BeNice()
            items = _c.items
            bids = _c.bids
            c = _c.contract
            typeID = None
            routeLength = 0
            if len(items) == 1:
                typeID = items[0].itemTypeID
            if c.startStationID == session.stationid:
                numJumps = 0
            elif c.startSolarSystemID == session.solarsystemid2:
                numJumps = 0
            elif c.startSolarSystemID not in jumpsCache:
                numJumps = pathfinderSvc.GetAutopilotJumpCount(session.solarsystemid2, c.startSolarSystemID)
                jumpsCache[c.startSolarSystemID] = numJumps
            else:
                numJumps = jumpsCache[c.startSolarSystemID]
            route = None
            if c.type == const.conTypeCourier:
                r = [c.startSolarSystemID, c.endSolarSystemID]
                r.sort()
                route = (r[0], r[1])
                if route not in routes:
                    routes[route] = pathfinderSvc.GetAutopilotJumpCount(c.startSolarSystemID, c.endSolarSystemID)
                routeLength = routes[route]
            startSecurityClass = None
            endSecurityClass = None
            if c.startSolarSystemID != session.solarsystemid2:
                startSecurityClass = int(securitySvc.get_modified_security_class(c.startSolarSystemID))
            if c.endSolarSystemID and c.endSolarSystemID != session.solarsystemid2:
                endSecurityClass = int(securitySvc.get_modified_security_class(c.endSolarSystemID))
            issuer = cfg.eveowners.Get(c.issuerCorpID if c.forCorp else c.issuerID).name
            startSystemName = cfg.evelocations.Get(c.startSolarSystemID).name
            endSystemName = cfg.evelocations.Get(c.endSolarSystemID).name
            contractTitle = GetContractTitle(c, items)
            getLabel = lambda columnName: localization.GetByLabel('UI/Contracts/ContractsSearch/%s' % columnName)
            d = {'contract': c,
             'title': contractTitle,
             'startSolarSystemName': startSystemName,
             'endSolarSystemName': endSystemName,
             'issuer': issuer,
             'searchresult': _c,
             'contractItems': items,
             'bids': bids,
             'rec': '',
             'text': '',
             'label': '',
             'typeID': typeID,
             'numJumps': numJumps,
             'routeLength': routeLength,
             'route': route,
             'startSecurityClass': startSecurityClass,
             'endSecurityClass': endSecurityClass,
             'dateIssued': c.dateIssued,
             'sort_%s' % getLabel('columnCurrentBid'): (c.price if not bids else bids[0].amount, c.contractID),
             'sort_%s' % getLabel('columnCollateral'): (c.collateral, c.contractID),
             'sort_%s' % getLabel('columnLocation'): (startSystemName, c.contractID),
             'sort_%s' % getLabel('columnPrice'): (int(c.price) or -int(c.reward), c.contractID),
             'sort_%s' % getLabel('columnReward'): (c.reward, c.contractID),
             'sort_%s' % getLabel('columnVolume'): (c.volume, c.contractID),
             'sort_%s' % getLabel('columnContract'): (contractTitle, c.contractID),
             'sort_%s' % getLabel('columnTimeLeft'): (c.dateExpired, c.contractID),
             'sort_%s' % getLabel('columnJumps'): (numJumps, c.contractID),
             'sort_%s' % getLabel('columPickup'): (startSystemName, c.contractID),
             'sort_%s' % getLabel('columnDropOff'): (endSystemName, c.contractID),
             'sort_%s' % getLabel('columnCreated'): c.dateIssued,
             'sort_%s' % getLabel('columnIssuer'): issuer.lower(),
             'sort_%s' % getLabel('columnBids'): bids,
             'sort_%s' % getLabel('columnRoute'): (routeLength, c.contractID),
             'sort_%s' % localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer'): c.title.lower()}
            data.append(d)

        self.numFound = numFound
        self.contractType = contractType
        self.pageData[self.currPage] = data
        self.RenderPage()
        self.contractsSvc.LogInfo('Found', numFound, 'contracts in %.4f seconds' % (searchTime / float(const.SEC)))

    def RenderPage(self):
        self.contractsSvc.IsStationInaccessible.clear_memoized()
        try:
            data = self.pageData[self.currPage]
            contractType = self.contractType
            if contractType == cc.CONTYPE_AUCTIONANDITEMECHANGE:
                contractType = const.conTypeItemExchange
            scrolllist = []
            entryType = {const.conTypeAuction: ContractEntrySearchAuction,
             const.conTypeItemExchange: ContractEntrySearchItemExchange,
             const.conTypeCourier: ContractEntrySearchCourier}[contractType]
            securityClassMe = sm.GetService('securitySvc').get_modified_security_class(session.solarsystemid2)
            ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
            numContractsFiltered = 0
            for d in data:
                contract = d['contract']
                if settings.user.ui.Get('contracts_search_client_maxjumps', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', None)
                    if maxNumJumps is not None and d['numJumps'] > maxNumJumps:
                        numContractsFiltered += 1
                        continue
                if d['route'] and settings.user.ui.Get('contracts_search_client_maxroute', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxroute_num', 0)
                    if maxNumJumps and d['routeLength'] > maxNumJumps:
                        numContractsFiltered += 1
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeunreachable', 1):
                    if d['numJumps'] > cc.NUMJUMPS_UNREACHABLE or d['routeLength'] > cc.NUMJUMPS_UNREACHABLE or self.contractsSvc.IsStationInaccessible(contract.startStationID) or self.contractsSvc.IsStationInaccessible(contract.endStationID):
                        numContractsFiltered += 1
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeignore', 1):
                    skipIt = False
                    for ownerID in ignoreList:
                        if ownerID in [contract.issuerID, contract.issuerCorpID]:
                            skipIt = True
                            break

                    if skipIt:
                        numContractsFiltered += 1
                        continue
                if settings.user.ui.Get('contracts_search_client_currentsecurity', False):
                    if d['startSecurityClass'] is not None and d['startSecurityClass'] != securityClassMe:
                        numContractsFiltered += 1
                        continue
                    if d['endSecurityClass'] is not None and d['endSecurityClass'] != securityClassMe:
                        numContractsFiltered += 1
                        continue
                scrolllist.append(GetFromClass(entryType, d))

            if contractType == const.conTypeItemExchange:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnPrice'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            elif contractType == const.conTypeAuction:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCurrentBid'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnBuyOut'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnBids'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            else:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columPickup'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnDropOff'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnReward'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCollateral'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnRoute'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            self.contractsScroll.sr.id = 'contractlist'
            self.contractsScroll.sr.minColumnWidth = {localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'): 100,
             localization.GetByLabel('UI/Contracts/ContractsSearch/columnBuyOut'): 200}
            self.contractsScroll.LoadContent(contentList=scrolllist, headers=columns, noContentHint=localization.GetByLabel('UI/Contracts/ContractsSearch/labelNoContractsFound'), ignoreSort=False, scrolltotop=True)
            txt = localization.GetByLabel('UI/Contracts/ContractsSearch/labelNumberContractsFound', num=self.numFound)
            if numContractsFiltered:
                txt += localization.GetByLabel('UI/Contracts/ContractsSearch/ContractsFilteredOut', numFilteredOut=numContractsFiltered)
            self.foundLabel.SetText(txt)
            self.UpdatePaging(self.currPage + 1, self.numPages)
        finally:
            self.IndicateLoading(loading=0)

    def IndicateLoading(self, loading = 0):
        try:
            if loading:
                self.loadingWheel.Show()
                self.contractsScroll.sr.maincontainer.opacity = 0.5
            else:
                self.loadingWheel.Hide()
                self.contractsScroll.sr.maincontainer.opacity = 1.0
        except:
            pass

    def DoNothing(self, *args):
        pass


class PageLink(Container):

    def __init__(self, parent, label, onClick, selected = False, align = uiconst.TOPLEFT, left = 0, name = None):
        self._label = label
        self._onClick = onClick
        self._selected = selected
        super(PageLink, self).__init__(name=name or 'PageLink', parent=parent, align=align, state=uiconst.UI_NORMAL, left=left, width=20, height=20)
        eveLabel.EveLabelMedium(parent=self, align=uiconst.CENTER, text=self._label, bold=self._selected)
        self._background = Fill(parent=self, align=uiconst.TOALL, opacity=0.05 if self._selected else 0.0)

    def OnMouseEnter(self, *args):
        if not self._selected:
            animations.FadeIn(self._background, endVal=0.2, duration=0.1)

    def OnMouseExit(self, *args):
        if not self._selected:
            animations.FadeTo(self._background, endVal=0.05 if self._selected else 0.0, duration=0.3)

    def OnClick(self, *args):
        if not self._selected:
            self._onClick()


class EditFieldVariables(object):

    def __init__(self, headerText, configName, fromConfigName, fromMaxValue, fromSettingName, toConfigName, toMaxValue, toSettingName):
        self.headerText = headerText
        self.configName = configName
        self.fromConfigName = fromConfigName
        self.fromMaxValue = fromMaxValue
        self.fromSettingName = fromSettingName
        self.toConfigName = toConfigName
        self.toMaxValue = toMaxValue
        self.toSettingName = toSettingName
