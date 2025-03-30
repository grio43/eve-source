#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpStoreFilters.py
import eveicon
from carbonui import uiconst, ButtonVariant
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.utilMenu import ExpandedUtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.station.loyaltyPointStore.lpStoreFiltersWindow import LPStoreFiltersWindow
from localization import GetByLabel

class LPStoreFiltersBase(Container):

    def ApplyAttributes(self, attributes):
        super(LPStoreFiltersBase, self).ApplyAttributes(attributes)
        self.corpID = attributes.corpID
        self._filterEditClearedCallback = attributes.filterEditClearedCallback
        self._filterEditCallback = attributes.filterEditCallback
        self.ConstructLayout()

    def ConstructLayout(self):
        raise NotImplementedError

    def GetCurrentFilters(self):
        raise NotImplementedError

    def Refresh(self):
        raise NotImplementedError

    def _OnFilterEditCleared(self):
        self._filterEditClearedCallback()

    def _OnFilterEdit(self):
        self._filterEditCallback()


class LPStoreFilters(LPStoreFiltersBase):

    def ApplyAttributes(self, attributes):
        self.lpSvc = sm.GetService('lpstore')
        super(LPStoreFilters, self).ApplyAttributes(attributes)

    def ConstructLayout(self):
        self.presetCombo = Combo(parent=self, name='presetCombo', align=uiconst.TOLEFT, width=180)
        self.filterPriceButton = Button(name='filterPriceButton', parent=self, variant=ButtonVariant.GHOST, label=GetByLabel('UI/LPStore/filterPrice'), align=uiconst.TOLEFT, func=self.OnPriceFilter, padLeft=8)
        self.filterEdit = QuickFilterEdit(name='filterField', parent=self, hintText=GetByLabel('UI/Common/Search'), maxLength=64, OnClearFilter=self._OnFilterEditCleared, align=uiconst.TORIGHT, padLeft=4, width=120, isTypeField=True)
        self.filterEdit.ReloadFunction = self._OnFilterEdit

    def GetCurrentFilters(self):
        filters = self.lpSvc.GetCurrentFilters()
        textFilter = self.filterEdit.GetValue().lstrip().lower()
        return (filters, textFilter)

    def Refresh(self):
        self.presetCombo.OnChange = self.OnPresetComboChange

    def RefreshPresets(self):
        options = [ (preset.label, preset.label) for preset in self.lpSvc.GetPresets() ]
        options.append((GetByLabel('UI/LPStore/EditFilters'), GetByLabel('UI/LPStore/EditFilters')))
        self.presetCombo.LoadOptions(options, select=self.lpSvc.GetCurrentPresetLabel())

    def OpenFilters(self):
        LPStoreFiltersWindow.Open(corpID=self.corpID)

    def OnPresetComboChange(self, _blah, _bleh, label):
        if label == GetByLabel('UI/LPStore/PresetNone') or label == GetByLabel('UI/LPStore/EditFilters'):
            self.OpenFilters()
        else:
            self.lpSvc.ChangeCurrentPreset(label)

    def OnPriceFilter(self, *_args):
        self.utilMenu = ExpandedUtilMenu(parent=uicore.layer.utilmenu, controller=self.filterPriceButton, menuAlign=uiconst.TOTOP, GetUtilMenu=self.GetPriceFilterUtilMenu)

    def GetPriceFilterUtilMenu(self, menuParent):
        innerCont = Container(parent=menuParent, align=uiconst.TOTOP, padTop=8, width=334, height=78)
        innerCont.GetEntryWidth = lambda mc = innerCont: 400
        lpRowCont = Container(name='lpRowCont', width=302, height=25, padding=8, align=uiconst.TOTOP, parent=innerCont)
        EveLabelMedium(parent=lpRowCont, text=GetByLabel('UI/LPStore/lpPriceRange'), align=uiconst.TOLEFT)
        lpRowMaxVal = SingleLineEditInteger(parent=lpRowCont, align=uiconst.TORIGHT, name='LPRowMaxVal', width=100, label=GetByLabel('UI/LPStore/max'))
        EveLabelSmall(text='-', parent=lpRowCont, align=uiconst.TORIGHT, padRight=2, top=3)
        lpRowMinVal = SingleLineEditInteger(parent=lpRowCont, align=uiconst.TORIGHT, name='LPRowMinVal', padRight=2, width=100, label=GetByLabel('UI/LPStore/min'))
        iskRowCont = Container(name='iskRowCont', width=302, height=25, padding=8, align=uiconst.TOTOP, parent=innerCont)
        EveLabelMedium(parent=iskRowCont, text=GetByLabel('UI/LPStore/iskPriceRange'), align=uiconst.TOLEFT)
        iskRowMaxVal = SingleLineEditInteger(parent=iskRowCont, align=uiconst.TORIGHT, name='iskRowMaxVal', width=100)
        EveLabelSmall(text='-', parent=iskRowCont, align=uiconst.TORIGHT, padRight=2, top=3)
        iskRowMinVal = SingleLineEditInteger(parent=iskRowCont, align=uiconst.TORIGHT, name='iskRowMinVal', width=100, padRight=2)
        filters = self.lpSvc.GetCurrentFilters()
        self.hookUpNumberEditField('minLP', lpRowMinVal, filters)
        self.hookUpNumberEditField('maxLP', lpRowMaxVal, filters)
        self.hookUpNumberEditField('minISK', iskRowMinVal, filters)
        self.hookUpNumberEditField('maxISK', iskRowMaxVal, filters)

    def hookUpNumberEditField(self, key, field, filters, defaultText = ''):
        initialValue = filters.get(key, None)
        if initialValue is None:
            field.SetText('')
        else:
            field.SetValue(initialValue)

        def MakeOnEditChangeFun(key):

            def OnEditChange(s):
                if s and s != '-':
                    val = int(s)
                    if val == 0:
                        self.lpSvc.RemoveFilter(key)
                    else:
                        self.lpSvc.AddFilters({key: int(s)})
                else:
                    self.lpSvc.RemoveFilter(key)

            return OnEditChange

        field.OnChange = MakeOnEditChangeFun(key)
