#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmppchatclient\pcownerpickerdialog.py
import localization
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.lib import appConst as const
from eveexceptions import UserError

class PCOwnerPickerDialog(Window):
    __guid__ = 'form.PCOwnerPickerDialog'
    default_windowID = 'PCOwnerPickerDialog'
    default_iconNum = 'res:/ui/Texture/WindowIcons/peopleandplaces.png'
    default_captionLabelPath = 'UI/Chat/SelectAllianceCorpChar'
    default_minSize = (355, 300)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ownerID = None
        self.searchStr = ''
        grid = LayoutGrid(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP), align=uiconst.TOPLEFT, columns=2, cellSpacing=(4, 4))
        self.sr.inpt = SingleLineEditText(name='edit', parent=grid, align=uiconst.CENTER, maxLength=37)
        Button(parent=grid, label=localization.GetByLabel('UI/Common/Buttons/Search'), func=self.Search, btn_default=1)
        self.sr.scroll = Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), multiSelect=False)
        self.sr.standardBtns = ButtonGroup(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, idx=0, btns=[[localization.GetByLabel('UI/Generic/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Generic/Cancel'),
          self.OnCancel,
          (),
          81]])

    def Search(self, *args):
        scrolllist = []
        results = []
        self.ShowLoad()
        try:
            hint = ''
            self.searchStr = self.GetSearchStr()
            self.SetHint()
            if len(self.searchStr) < 1:
                hint = localization.GetByLabel('UI/Common/PleaseTypeSomething')
                return
            result = sm.RemoteSvc('lookupSvc').LookupOwners(self.searchStr, 0)
            if result is None or not len(result):
                hint = localization.GetByLabel('UI/Chat/NoAllianceCorpCharFound', searchStr=self.searchStr)
                return
            for r in result:
                results.append(r.ownerID)

            cfg.eveowners.Prime(results)
            for r in result:
                scrolllist.append(GetFromClass(SearchEntry, {'label': r.ownerName,
                 'typeID': r.typeID,
                 'itemID': r.ownerID,
                 'confirmOnDblClick': 1,
                 'listvalue': [r.ownerName, r.ownerID]}))

        finally:
            self.sr.scroll.Load(fixedEntryHeight=18, contentList=scrolllist)
            self.SetHint(hint)
            self.HideLoad()

    def GetSearchStr(self):
        return self.sr.inpt.GetValue().strip()

    def Confirm(self):
        self.OnOK()

    def ValidateOK(self):
        if self.searchStr != self.GetSearchStr():
            self.Search()
            return False
        if self.ownerID is None:
            return False
        return True

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def OnOK(self, *args):
        sel = self.sr.scroll.GetSelected()
        if sel:
            self.ownerID = sel[0].itemID
            self.CloseByUser()
        else:
            info = localization.GetByLabel('UI/Chat/MustSelectOneChoice')
            raise UserError('CustomInfo', {'info': info})

    def OnCancel(self, *args):
        self.ownerID = None
        self.CloseByUser()


class SearchEntry(Item):
    __guid__ = 'listentry.SearchEntry'

    def GetMenu(self, *args):
        scroll = self.sr.node.scroll
        scroll.DeselectAll()
        scroll.SelectNode(self.sr.node)
        return []

    def GetHint(self):
        return ''
