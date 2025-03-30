#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\quickFilter.py
import blue
import eveicon
import localization
import evetypes
import uthread
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText

def GetRecName(rec):
    name = ''
    if hasattr(rec, 'name'):
        name = rec.name.lower()
    elif hasattr(rec, 'contactID'):
        name = cfg.eveowners.Get(rec.contactID).name
        name = name.lower()
    elif hasattr(rec, 'invtype'):
        name = rec.invtype.typeName.lower()
    elif hasattr(rec, 'typeID'):
        name = evetypes.GetName(rec.typeID).lower()
    return name


class QuickFilterEdit(SingleLineEditText):
    __guid__ = 'uicls.QuickFilterEdit'
    default_width = 100
    default_left = 0
    default_top = 0
    default_icon = eveicon.search

    def ApplyAttributes(self, attributes):
        attributes.hintText = attributes.hintText or localization.GetByLabel('UI/Common/Search')
        attributes.maxLength = attributes.maxLength or 37
        if 'callback' in attributes:
            self.ReloadFunction = attributes.callback
        super(QuickFilterEdit, self).ApplyAttributes(attributes)
        self.ShowClearButton(hint=localization.GetByLabel('UI/Calendar/Hints/Clear'))
        self.RefreshTextClipper()
        self.filterThread = None
        self.lastStrFilter = None
        self.quickFilterInput = None
        self.OnChange = self.SetQuickFilterInput
        self.OnReturn = self.RegisterInput
        self.OnFocusLost = self.RegisterInput
        self.OnClearFilter = attributes.OnClearFilter
        if attributes.get('triggerFilterOnCreation', True):
            self.SetQuickFilterInput()

    def OnClearButtonClick(self, *args, **kwds):
        super(QuickFilterEdit, self).OnClearButtonClick()
        if self.OnClearFilter:
            self.OnClearFilter()

    def GetValue(self, *args, **kwds):
        return super(QuickFilterEdit, self).GetValue(registerHistory=False)

    def RegisterInput(self, *args, **kwds):
        self.RegisterHistory()
        self.DoReload()

    def SetQuickFilterInput(self, *args):
        if self.filterThread is not None and self.filterThread.alive:
            return
        self.filterThread = uthread.new(self._SetQuickFilterInput)

    def _SetQuickFilterInput(self):
        try:
            blue.pyos.synchro.Sleep(400)
        finally:
            self.filterThread = None

        self.DoReload()

    def DoReload(self):
        strFilter = self.GetValue()
        if self.lastStrFilter == strFilter:
            return
        self.lastStrFilter = strFilter
        if len(strFilter) > 0:
            self.quickFilterInput = strFilter.lower()
            self.ReloadFunction()
        else:
            prefilter = self.quickFilterInput
            self.quickFilterInput = None
            if prefilter != None:
                self.ReloadFunction()

    def ReloadFunction(self, *args):
        pass

    def QuickFilter(self, rec):
        if not self.quickFilterInput:
            return False
        name = GetRecName(rec)
        input = self.quickFilterInput.lower()
        return name.find(input) + 1
