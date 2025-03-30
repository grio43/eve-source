#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\noneNPCAccountOwnerDialog.py
import localization
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.lib import appConst as const

class NoneNPCAccountOwnerDialog(Window):
    default_width = 320
    default_height = 300
    default_minSize = (default_width, default_height)
    default_windowID = 'NoneNPCAccountOwnerDialog'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporation.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ownerID = None
        self.searchStr = ''
        self.Confirm = self.ValidateOK
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=70, clipChildren=True)
        self.sr.errorParent = Container(name='errorParent', align=uiconst.TOBOTTOM, height=16, parent=self.sr.main, state=uiconst.UI_HIDDEN)
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.Startup()
        self.sr.scroll.multiSelect = 0
        self.sr.standardBtns = ButtonGroup(parent=self.GetMainArea(), btns=[[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]], idx=self.topParent.GetOrder() + 1)
        self.SetCaption(localization.GetByLabel('UI/Wallet/WalletWindow/SelectCorpOrChar'))
        self.label = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Shared/TypeSearchString'), parent=self.topParent, left=70, top=16, state=uiconst.UI_NORMAL)
        inpt = SingleLineEditText(name='edit', parent=self.topParent, pos=(70,
         self.label.top + self.label.height + 2,
         120,
         0), align=uiconst.TOPLEFT, maxLength=32)
        inpt.OnReturn = self.Search
        self.sr.inpt = inpt
        Button(parent=self.topParent, label=localization.GetByLabel('UI/Wallet/WalletWindow/WalletSearch'), pos=(inpt.left + inpt.width + 8,
         inpt.top,
         0,
         0), func=self.Search, btn_default=1)
        self.SetHint(localization.GetByLabel('UI/Common/TypeInSearch'))

    def Search(self, *args):
        scrolllist = []
        self.ShowLoad()
        try:
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                self.SetHint(localization.GetByLabel('UI/Shared/PleaseTypeSomething'))
                return
            result = sm.RemoteSvc('lookupSvc').LookupNoneNPCAccountOwners(self.searchStr, 0)
            if result is None or not len(result):
                self.SetHint(localization.GetByLabel('UI/Wallet/WalletWindow/NoCorpCharFound', searchString=self.searchStr))
                return
            cfg.eveowners.Prime([ each.ownerID for each in result ])
            for each in result:
                owner = cfg.eveowners.Get(each.ownerID)
                scrolllist.append(GetFromClass(Item, {'label': owner.name,
                 'typeID': owner.typeID,
                 'itemID': each.ownerID,
                 'confirmOnDblClick': 1,
                 'OnClick': self.CheckSelected,
                 'listvalue': [owner.name, each.ownerID]}))

        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Wallet/WalletWindow/SearchNoResults'))
            self.CheckSelected()
            self.HideLoad()

    def GetSearchStr(self):
        return self.sr.inpt.GetValue().strip()

    def Confirm(self):
        self.OnOK()

    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return 0
        if self.ownerID is None:
            return 0
        return 1

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()

    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()

    def CheckSelected(self, *args):
        sel = 1
        if len(self.sr.scroll.GetNodes()) > 0:
            sel = self.sr.scroll.GetSelected()
        self.DisplayPickHint(bool(sel))

    def DisplayPickHint(self, off = 1):
        ep = self.sr.errorParent
        ep.state = uiconst.UI_HIDDEN
        ep.Flush()
        if off:
            ep.state = uiconst.UI_HIDDEN
        else:
            text = localization.GetByLabel('UI/Wallet/WalletWindow/SelectCharacterOrCorp')
            t = eveLabel.EveLabelMedium(text=text, top=-3, parent=ep, width=self.minsize[0] - 32, state=uiconst.UI_DISABLED, color=(1.0, 0.0, 0.0, 1.0), align=uiconst.CENTER)
            ep.state = uiconst.UI_DISABLED
            ep.height = t.height + 8
