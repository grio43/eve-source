#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\all_ui_rankings.py
import carbonui.const as uiconst
import localization
import log
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from eve.common.lib import appConst as const

class FormAlliancesRankings(Container):
    is_loaded = False

    def Load(self, *args):
        if self.is_loaded:
            return
        self.is_loaded = True
        self.toolbarContainer = ContainerAutoSize(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        buttonLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ShowAll')
        buttonOptions = [[buttonLabel,
          self.ShowRankings,
          (0,),
          81]]
        btns = ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
        self.sr.mainBtns = btns
        self.sr.scroll = eveScroll.Scroll(parent=self)
        self.ShowRankings()

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ShowRankings(self, maxLen = 100):
        log.LogInfo('ShowRankings', maxLen)
        if maxLen == 0 and eve.Message('ConfirmShowAllRankedAlliances', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        try:
            sm.GetService('corpui').ShowLoad()
            headers = [localization.GetByLabel('UI/Common/Name'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ExecutorCorp'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ShortName'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/Created'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Members'),
             localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/AllianceStanding')]
            scrolllist = []
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NoRankingsFound')
            if self is None or self.destroyed:
                log.LogInfo('ShowRankings Destroyed or None')
            else:
                data = sm.GetService('alliance').GetRankedAlliances(maxLen)
                rows = data.alliances
                owners = []
                for row in rows:
                    if row.executorCorpID not in owners:
                        owners.append(row.executorCorpID)

                if len(owners):
                    cfg.eveowners.Prime(owners)
                for row in rows:
                    standing = data.standings.get(row.allianceID, 0)
                    self.__AddToList(row, standing, scrolllist)

            self.sr.scroll.adjustableColumns = 1
            self.sr.scroll.sr.id = 'alliances_rankings'
            noFoundLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NoRankingsFound')
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noFoundLabel)
        finally:
            sm.GetService('corpui').HideLoad()

    def __GetLabel(self, row, standing):
        executor = None
        if row.executorCorpID is not None:
            executor = cfg.eveowners.GetIfExists(row.executorCorpID)
        if executor is not None:
            executorCorpName = executor.ownerName
        else:
            executorCorpName = ''
        if standing is None:
            standing = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/NotSet')
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (row.allianceName,
         executorCorpName,
         row.shortName,
         FmtDate(row.startDate, 'ls'),
         row.memberCount,
         standing)
        return label

    def __AddToList(self, ranking, standing, scrolllist):
        scrolllist.append(GetFromClass(Generic, {'label': self.__GetLabel(ranking, standing),
         'ranking': ranking,
         'GetMenu': self.GetRankingMenu}))

    def GetRankingMenu(self, entry):
        allianceID = entry.sr.node.ranking.allianceID
        res = GetMenuService().GetMenuFromItemIDTypeID(allianceID, const.typeAlliance)
        joinLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ApplyToJoin')
        if self._CanApplyToJoinAlliances():
            res.append([joinLabel, [[joinLabel, sm.GetService('corpui').ApplyToJoinAlliance, [allianceID]]]])
        else:
            log.LogInfo('Apply to join', allianceID, 'will be disabled as pre-reqs for joining are not met')
            res.append([joinLabel, [[joinLabel, sm.GetService('corpui').ApplyToJoinAlliance, [allianceID]]], [-1]])
        return res

    @staticmethod
    def _CanApplyToJoinAlliances():
        try:
            return sm.GetService('corp').CheckCanApplyToJoinAlliance()
        except UserError:
            return False
