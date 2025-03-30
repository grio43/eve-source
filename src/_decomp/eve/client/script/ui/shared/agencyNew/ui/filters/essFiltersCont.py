#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\essFiltersCont.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from carbonui.control.section import SubSectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.structure.structureSettings.uiSettingUtil import SinglelineEditIntegerWithUnit
from localization import GetByLabel
from marketutil.const import MAX_ORDER_PRICE

class ESSFiltersCont(BaseFiltersCont):
    default_name = 'ESSFiltersCont'

    def ConstructFilters(self):
        settings = sm.RemoteSvc('dynamicResourceCacheMgr').GetDynamicResourceSettings()
        self.maxOutput = settings['maxOutput'] * 100.0
        self.minOutput = settings['minOutput'] * 100.0
        self.ConstructDistanceCombo()
        self.ConstructCustomFilterSubsection()
        self.ConstructBountiesOutputFilter()
        self.ConstructMainBankFilter()
        self.ConstructReserveBankUnlockedFilter()
        self.ConstructReserveBankFilter()
        self.ConstructDataDelayNotice()

    def ConstructDataDelayNotice(self):
        EveLabelLarge(text=GetByLabel('UI/Agency/ESS/DataDelayNotice'), parent=self.filtersCont, align=uiconst.TOTOP, padding=(5, 7, 5, 5))

    def ConstructCustomFilterSubsection(self):
        self.customFilterSection = SubSectionAutoSize(headerText=GetByLabel('UI/Agency/ESS/BankFilters'), parent=self.filtersCont, align=uiconst.TOTOP)
        self.customFilterSection.caption.uppercase = False

    def ConstructReserveBankUnlockedFilter(self):
        reserveBankUnlockedFilterContainer = Container(name='reserveBankUnlockedFilterContainer', parent=self.customFilterSection, align=uiconst.TOTOP, height=30, top=5)
        EveLabelMedium(name='reserveBankUnlockedLabel', parent=ContainerAutoSize(parent=reserveBankUnlockedFilterContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, text='%s:' % GetByLabel('UI/Agency/ESS/ReserveBankUnlocked'))
        Checkbox(name='reserveBankUnlockedCheckbox', parent=reserveBankUnlockedFilterContainer, align=uiconst.TORIGHT, checked=self.IsReserveBankUnlockedFilterEnabled(), callback=self.OnReserveBankUnlockedCheckbox, left=5)

    def ConstructReserveBankFilter(self):
        reserveBankFilterContainer = Container(name='reserveBankFilterContainer', parent=self.customFilterSection, align=uiconst.TOTOP, height=30, top=5)
        EveLabelMedium(name='reserveBankAmountLabel', parent=ContainerAutoSize(parent=reserveBankFilterContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, text='%s:' % GetByLabel('UI/Agency/ESS/MinReserveBankAmount'), maxWidth=120)
        Checkbox(name='minReserveBankAmountFilterEnabledCheckbox', parent=reserveBankFilterContainer, align=uiconst.TORIGHT, checked=self.IsMinReserveBankAmountFilterEnabled(), callback=self.OnMinReserveBankAmountCheckbox, left=5)
        minReserveBankAmountEditContainer = ContainerAutoSize(name='minReserveBankAmountEditContainer', parent=reserveBankFilterContainer, align=uiconst.TORIGHT, left=10)
        self.minReserveBankAmountEdit = SingleLineEditInteger(name='minReserveBankAmountEdit', parent=minReserveBankAmountEditContainer, align=uiconst.CENTER, width=100, top=0, OnChange=self.OnMinReserveBankAmountChanged, setvalue=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNT), maxValue=MAX_ORDER_PRICE, dataType=long, showNumericControls=False)

    def ConstructMainBankFilter(self):
        mainBankFilterContainer = Container(name='mainBankFilterContainer', parent=self.customFilterSection, align=uiconst.TOTOP, height=30, top=10)
        EveLabelMedium(name='mainBankAmountLabel', parent=ContainerAutoSize(parent=mainBankFilterContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, text='%s:' % GetByLabel('UI/Agency/ESS/MinMainBankAmount'), maxWidth=120)
        Checkbox(name='minMainBankAmountFilterEnabledCheckbox', parent=mainBankFilterContainer, align=uiconst.TORIGHT, checked=self.IsMinMainBankAmountFilterEnabled(), callback=self.OnMinMainBankAmountCheckbox, left=5)
        minMainBankAmountEditContainer = ContainerAutoSize(name='minMainBankAmountEditContainer', parent=mainBankFilterContainer, align=uiconst.TORIGHT, left=10)
        self.minMainBankAmountEdit = SingleLineEditInteger(name='minMainBankAmountEdit', parent=minMainBankAmountEditContainer, align=uiconst.CENTER, width=100, top=0, OnChange=self.OnMinMainBankAmountChanged, setvalue=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNT), maxValue=MAX_ORDER_PRICE, dataType=long, showNumericControls=False)

    def ConstructBountiesOutputFilter(self):
        bountiesFilterContainer = Container(name='bountiesFilterContainer', parent=self.customFilterSection, align=uiconst.TOTOP, height=40, padTop=16)
        Checkbox(name='bountiesFilterEnabledCheckbox', parent=bountiesFilterContainer, align=uiconst.TORIGHT, checked=self.IsBountiesOutputFilterEnabled(), callback=self.OnBountiesOutputCheckbox, left=5)
        EveLabelMedium(name='bountiesOutputLabel', parent=bountiesFilterContainer, align=uiconst.TOPLEFT, text='%s:' % GetByLabel('UI/Agency/ESS/BountiesOutput'), maxWidth=100)
        editsContainer = Container(name='editsContainer', parent=bountiesFilterContainer, align=uiconst.TOTOP, height=SingleLineEditInteger.default_height, padRight=10)
        self.maxBountyEdit = SinglelineEditIntegerWithUnit(name='maxBountyEdit', parent=editsContainer, align=uiconst.TORIGHT, minValue=self.minOutput, maxValue=self.maxOutput, width=60, unit='%', padLeft=8, label=GetByLabel('UI/Common/Max'), OnChange=self.OnMaxBountyEditChanged, setvalue=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMAXBOUNTY), fadeOutContent=False)
        self.minBountyEdit = SinglelineEditIntegerWithUnit(name='minBountyEdit', parent=editsContainer, align=uiconst.TORIGHT, minValue=self.minOutput, maxValue=self.maxOutput, width=60, unit='%', label=GetByLabel('UI/Common/Min'), OnChange=self.OnMinBountyEditChanged, setvalue=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINBOUNTY), fadeOutContent=False)

    def IsReserveBankUnlockedFilterEnabled(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSRESERVEBANKUNLOCKED)

    def OnReserveBankUnlockedCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSRESERVEBANKUNLOCKED, checkbox.GetValue())

    def IsMinMainBankAmountFilterEnabled(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNTFILTERENABLED)

    def IsMinReserveBankAmountFilterEnabled(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNTFILTERENABLED)

    def OnMinMainBankAmountCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNTFILTERENABLED, checkbox.GetValue())

    def OnMinReserveBankAmountCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNTFILTERENABLED, checkbox.GetValue())

    def OnMinMainBankAmountChanged(self, text):
        if not self.IsTextValid(text):
            return
        if self.IsMinMainBankAmountFilterEnabled():
            setFilterFunc = agencyFilters.SetFilterValue
        else:
            setFilterFunc = agencyFilters.SetFilterValueWithoutEvent
        setFilterFunc(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINMAINBANKAMOUNT, long(text))

    def OnMinReserveBankAmountChanged(self, text):
        if not self.IsTextValid(text):
            return
        if self.IsMinReserveBankAmountFilterEnabled():
            setFilterFunc = agencyFilters.SetFilterValue
        else:
            setFilterFunc = agencyFilters.SetFilterValueWithoutEvent
        setFilterFunc(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINRESERVEBANKAMOUNT, long(text))

    def IsTextValid(self, text):
        if text is None or len(text) < 1:
            return False
        return True

    def IsBountiesOutputFilterEnabled(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSBOUNTYFILTERENABLED)

    def OnBountiesOutputCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ESSBOUNTYFILTERENABLED, checkbox.GetValue())

    def OnMinBountyEditChanged(self, text):
        if len(text) < 1:
            return
        minValue = int(text)
        if self.maxBountyEdit.GetValue() < minValue:
            self.maxBountyEdit.SetValue(minValue)
        if self.IsBountiesOutputFilterEnabled():
            setFilterFunc = agencyFilters.SetFilterValue
        else:
            setFilterFunc = agencyFilters.SetFilterValueWithoutEvent
        setFilterFunc(self.contentGroupID, agencyConst.FILTERTYPE_ESSMINBOUNTY, text)

    def OnMaxBountyEditChanged(self, text):
        if len(text) < 1:
            return
        if self.IsBountiesOutputFilterEnabled():
            setFilterFunc = agencyFilters.SetFilterValue
        else:
            setFilterFunc = agencyFilters.SetFilterValueWithoutEvent
        setFilterFunc(self.contentGroupID, agencyConst.FILTERTYPE_ESSMAXBOUNTY, text)
