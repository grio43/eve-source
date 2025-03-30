#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\corporationOrAlliancePickerDailog.py
import logging
import localization
from carbonui import const as uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
log = logging.getLogger(__name__)

class CorporationOrAlliancePickerDailog(Window):
    __guid__ = 'form.CorporationOrAlliancePickerDailog'
    default_windowID = 'CorporationOrAlliancePickerDailog'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporation.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ownerID = None
        self.searchStr = ''
        self.searchAttr = attributes.Get('searchStr', '')
        self.SetScope(uiconst.SCOPE_INGAME)
        self.Confirm = self.ValidateOK
        strTitle = localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/SelectWarableCorpOrAlliance')
        self.SetCaption(strTitle)
        self.SetMinSize([320, 300])
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.sr.standardBtns = ButtonGroup(parent=self.GetMainArea(), btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Generic/Cancel'),
          self.OnCancel,
          (),
          81]], idx=self.topParent.GetOrder() + 1)
        self.sr.txtWarning = eveLabel.EveLabelMedium(parent=self.sr.main, align=uiconst.TOBOTTOM, top=0, padding=4, color=[1,
         0,
         0,
         1], state=uiconst.UI_HIDDEN)
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=const.defaultPadding)
        self.sr.scroll.multiSelect = False
        self.sr.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.label = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Shared/TypeSearchString'), parent=self.topParent, left=70, top=5, state=uiconst.UI_NORMAL)
        inpt = self.sr.inpt = SingleLineEditText(name='edit', parent=self.topParent, left=70, top=self.label.top + self.label.height + 2, width=86, align=uiconst.TOPLEFT, maxLength=32, setvalue=self.searchAttr)
        inpt.OnReturn = self.Search
        Button(parent=self.topParent, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/Search'), pos=(inpt.left + inpt.width + 2,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)
        self.sr.exactChkBox = Checkbox(text=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/SearchExact'), parent=self.topParent, settingsKey='SearchExactChk', align=uiconst.TOPLEFT, pos=(inpt.left,
         inpt.top + inpt.height,
         200,
         0))
        self.topParent.height = max(52, self.sr.exactChkBox.top + self.sr.exactChkBox.height)
        if self.searchAttr:
            self.Search()

    def Search(self, *args):
        scrolllist = []
        self.ShowLoad()
        self.sr.txtWarning.state = uiconst.UI_HIDDEN
        try:
            groupID, exact = const.groupCorporation, self.sr.exactChkBox.GetValue()
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                self.SetHint(localization.GetByLabel('UI/Shared/PleaseTypeSomething'))
                return
            warableResultByID, _ = sm.GetService('war').SearchForWarableEntity(self.searchStr, exact)
            if warableResultByID is None or not len(warableResultByID):
                if exact:
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/ExactCorpOrAllianceNameNotFound', searchString=self.searchStr))
                else:
                    self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/CorpOrAllianceNameNotFound', searchString=self.searchStr))
                return
            cfg.eveowners.Prime([ ownerID for ownerID in warableResultByID.iterkeys() ])
            for each in warableResultByID.itervalues():
                owner = cfg.eveowners.Get(each.ownerID)
                scrolllist.append(GetFromClass(Item, {'label': owner.ownerName,
                 'OnDblClick': self.OnOK,
                 'typeID': owner.typeID,
                 'itemID': each.ownerID,
                 'confirmOnDblClick': 1,
                 'listvalue': [owner.ownerName, each.ownerID]}))

        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
            self.HideLoad()

    def GetSearchStr(self):
        if self.searchAttr and self.sr.inpt.GetValue() == '':
            return self.searchAttr
        return self.sr.inpt.GetValue().strip()

    def Confirm(self):
        self.OnOK()

    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return 0
        log.info('ValidateOK')
        if self.ownerID is None:
            return 0
        return 1

    def SetHint(self, hintstr = None):
        if hintstr is not None:
            self.sr.txtWarning.text = hintstr
            self.sr.txtWarning.state = uiconst.UI_DISABLED
        else:
            self.sr.txtWarning.state = uiconst.UI_HIDDEN

    def HideHint(self):
        self.sr.txtWarning.state = uiconst.UI_HIDDEN

    def OnScrollSelectionChange(self, *args):
        self.HideHint()

    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()
        else:
            self.SetHint(localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/ErrorPleaseChoose'))

    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()
