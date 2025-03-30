#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_killreports.py
import eveicon
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.neocom.charsheet.charSheetUtil import GetCombatEntries
from localization import GetByLabel
NUM_KILL_ENTRIES = 25
SHOW_KILLS = 0
SHOW_LOSSES = 1

class CorpKillReports(Container):
    default_name = 'killReportsCont'
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.prevIDs = []
        self.combatPageNum = 0
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=QuickFilterEdit.default_height)
        self.killReportQuickFilter = QuickFilterEdit(parent=self.topCont, align=uiconst.TORIGHT, width=150)
        self.killReportQuickFilter.ReloadFunction = self.ReloadKillReports
        self.ConstructPaginationButtons()
        combatValues = ((GetByLabel('UI/Corporations/Wars/Killmails/ShowKills'), SHOW_KILLS), (GetByLabel('UI/Corporations/Wars/Killmails/ShowLosses'), SHOW_LOSSES))
        selectedCombatType = settings.user.ui.Get('CorpCombatLogCombo', SHOW_KILLS)
        self.combatCombo = Combo(parent=self.topCont, name='combatCombo', select=selectedCombatType, align=uiconst.TOPLEFT, callback=self.OnCombatChange, options=combatValues, idx=0, adjustWidth=True)
        self.killReportsScroll = Scroll(parent=self, padding=(0, 8, 0, 0), id='killReportsScroll')

    def Load(self, *args):
        self.ShowReports()

    def ConstructPaginationButtons(self):
        self.btnContainer = ContainerAutoSize(name='pageBtnContainer', parent=self.topCont, align=uiconst.TORIGHT, height=ButtonIcon.default_height, padRight=4)
        self.prevBtn = ButtonIcon(parent=self.btnContainer, align=uiconst.CENTERLEFT, texturePath=eveicon.navigate_back, iconSize=16, hint=GetByLabel('UI/Common/Previous'))
        self.prevBtn.Disable()
        self.nextBtn = ButtonIcon(parent=self.btnContainer, align=uiconst.CENTERLEFT, texturePath=eveicon.navigate_forward, left=24, iconSize=16, hint=GetByLabel('UI/Common/ViewMore'))
        self.nextBtn.Disable()

    def OnCombatChange(self, *args):
        self.combatPageNum = 0
        self.ShowReports()

    def ShowReports(self, offset = None):
        combatSetting = self.combatCombo.GetValue()
        settings.user.ui.Set('CorpCombatLogCombo', combatSetting)
        if combatSetting == SHOW_KILLS:
            self.ShowCombatKills(offset)
        else:
            self.ShowCombatLosses(offset)

    def ReloadKillReports(self):
        if self.prevIDs and self.combatPageNum:
            offset = self.prevIDs[self.combatPageNum]
        else:
            offset = None
        self.ShowReports(offset)

    def ShowCombatKills(self, offset = None, pageChange = 0, *args):
        recent = sm.GetService('corp').GetRecentKills(NUM_KILL_ENTRIES, offset)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatKills, 'kills', pageNum=self.combatPageNum)

    def ShowCombatLosses(self, offset = None, pageChange = 0, *args):
        recent = sm.GetService('corp').GetRecentLosses(NUM_KILL_ENTRIES, offset)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatLosses, 'losses', pageNum=self.combatPageNum)

    def ShowKillsEx(self, recent, func, combatType, pageNum):
        filterText = self.killReportQuickFilter.GetValue().strip().lower()
        scrolllist, headers = GetCombatEntries(recent, filterText=filterText)
        killIDs = [ k.killID for k in recent ]
        if pageNum > 0:
            self.prevBtn.Enable()
            pageIndex = min(pageNum, len(self.prevIDs) - 1)
            offset = self.prevIDs[pageIndex - 1]
            self.prevBtn.OnClick = (func, offset, -1)
        else:
            self.prevBtn.Disable()
        if pageNum + 1 > len(self.prevIDs):
            maxKillIDs = max(killIDs) + 1 if killIDs else 0
            self.prevIDs.append(maxKillIDs)
        if len(recent) >= NUM_KILL_ENTRIES:
            self.nextBtn.Enable()
            self.nextBtn.OnClick = (func, min(killIDs), 1)
        else:
            self.nextBtn.Disable()
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = GetByLabel('UI/Corporations/CorporationWindow/Wars/NoKillsFound')
        elif combatType == 'losses':
            noContentHintText = GetByLabel('UI/Corporations/CorporationWindow/Wars/NoLossesFound')
        self.killReportsScroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHintText)
