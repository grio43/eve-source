#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warHistoryCont.py
import uthread
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.container import Container
import blue
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from menu import MenuLabel
from eve.client.script.ui.control.eveIcon import GetOwnerLogo
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.corporation.war.warEntry import OpenWarReport
from eveservices.menu import GetMenuService
from evewar.const import PEACE_REASON_WAR_SURRENDER, PEACE_REASON_HQ_REMOVED, PEACE_REASON_HQ_OWNER_LEFT_ALLIANCE, PEACE_REASON_CORP_LEFT_ALLIANCE
from localization import GetByLabel
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui import const as uiconst
from utillib import KeyVal

class WarHistoryCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.historyScroll = Scroll(parent=self)

    def Load(self, *args):
        self.LoadHistory()

    def LoadHistory(self):
        (outgoingTreaties, incomingTreaties), corpWars, allianceWars = uthread.parallel([(self.GetPeaceTreaties, ()), (self.GetCorpWars, ()), (self.GetAllianceWars, ())])
        allWars = corpWars + allianceWars
        currentTime = blue.os.GetWallclockTime()
        finishedWars = []
        for eachWar in allWars:
            warFinished = eachWar.timeFinished
            if warFinished and warFinished < currentTime:
                finishedWars.append(eachWar)

        treatiesEntries = self.GetTreatiesGroup(outgoingTreaties, incomingTreaties)
        finishedWarsEntries = self.GetWarScrollList(finishedWars)
        contentList = treatiesEntries + finishedWarsEntries
        self.historyScroll.Load(contentList=contentList)

    def GetPeaceTreaties(self):
        return sm.GetService('war').GetPeaceTreaties()

    def GetCorpWars(self):
        return sm.RemoteSvc('warsInfoMgr').GetWarsByOwnerID(session.corpid)

    def GetAllianceWars(self):
        if not session.allianceid:
            return []
        return sm.RemoteSvc('warsInfoMgr').GetWarsByOwnerID(session.allianceid)

    def GetTreatiesGroup(self, outgoingTreaties, incomingTreaties):
        if not outgoingTreaties and not incomingTreaties:
            return []
        numTreaties = len(outgoingTreaties) + len(incomingTreaties)
        numUniqueOwners = len({treaty.otherOwnerID for treaty in outgoingTreaties + incomingTreaties})
        return [GetFromClass(ListGroup, {'GetSubContent': self.GetTreatiesSubContent,
          'label': GetByLabel('UI/Corporations/Wars/PeaceTreatiesGroup', numTreaties=numTreaties, numUniqueOwners=numUniqueOwners),
          'id': ('peaceTreaties', 0),
          'state': 'locked',
          'BlockOpenWindow': 1,
          'showicon': 'hide',
          'showlen': 0,
          'outgoingTreaties': outgoingTreaties,
          'incomingTreaties': incomingTreaties,
          'updateOnToggle': 0,
          'sublevel': 0})]

    def GetTreatiesSubContent(self, nodedata, *args):
        outgoingTreaties = nodedata.outgoingTreaties
        incomingTreaties = nodedata.incomingTreaties
        toPrime = {treaty.otherOwnerID for treaty in outgoingTreaties + incomingTreaties}
        cfg.eveowners.Prime(toPrime)
        scrollList = []
        corpOrAlliance = session.allianceid or session.corpid
        for treaties, peaceLabelName in [(outgoingTreaties, 'UI/Corporations/Wars/PeaceUntilAttackerText'), (incomingTreaties, 'UI/Corporations/Wars/PeaceUntilDefenderText')]:
            for treaty in treaties:
                reasonText = self.GetPeaceReasonText(treaty.peaceReason)
                ownerInfo = cfg.eveowners.Get(treaty.otherOwnerID)
                corpOrAllianceLink = GetShowInfoLink(ownerInfo.typeID, ownerInfo.ownerName, treaty.otherOwnerID)
                if reasonText:
                    label = GetByLabel('UI/Corporations/Wars/ForcedPeaceWithEntityWithReason', corpOrAllianceLink=corpOrAllianceLink, reason=reasonText)
                else:
                    label = GetByLabel('UI/Corporations/Wars/ForcedPeaceWithEntityWithoutReason', corpOrAllianceLink=corpOrAllianceLink)
                peaceDate = FmtDate(treaty.expiryDate)
                expireText = GetByLabel(peaceLabelName, peaceUntilDate=peaceDate)
                entry = GetFromClass(TreatyEntry, {'ownerInfo': ownerInfo,
                 'label': label,
                 'expireText': expireText,
                 'selectable': False,
                 'warID': treaty.warID})
                scrollList.append(entry)

        return scrollList

    @staticmethod
    def GetPeaceReasonText(peaceReason):
        if peaceReason == PEACE_REASON_WAR_SURRENDER:
            return GetByLabel('UI/Corporations/Wars/PeaceWarWasSurrendered')
        elif peaceReason in (PEACE_REASON_HQ_REMOVED, PEACE_REASON_HQ_OWNER_LEFT_ALLIANCE, PEACE_REASON_CORP_LEFT_ALLIANCE):
            return GetByLabel('UI/Corporations/Wars/PeaceHeadquartersUnavailable')
        else:
            return None

    def GetWarScrollList(self, wars, *args):
        warGroup = sm.GetService('info').GetFinishedWarsGroup(sorted(wars, key=lambda w: w.timeFinished), GetByLabel('UI/Corporations/Wars/FinishedWars'), 'finishedWarsHistory')
        return [warGroup]


class TreatyEntry(SE_BaseClassCore):
    ENTRYHEIGHT = 42
    isDragObject = True

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        iconSize = 32
        textLeft = iconSize + 6
        self.ownerLogoCont = Container(parent=self, pos=(0,
         0,
         iconSize,
         iconSize), name='ownerLogoCont', state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.nameLabel = EveLabelMedium(text='', name='nameLabel', parent=self, state=uiconst.UI_NORMAL, padLeft=textLeft, align=uiconst.TOTOP, maxLines=1, top=4)
        self.expiryTimeLabel = EveLabelMedium(text='', name='nameLabel', parent=self, state=uiconst.UI_DISABLED, padLeft=textLeft, align=uiconst.TOTOP, maxLines=1)

    def Load(self, node):
        self.sr.node = node
        ownerID = node.ownerInfo.ownerID
        self.nameLabel.text = node.label
        self.expiryTimeLabel.text = node.expireText
        self.LoadPortrait(ownerID)

    def LoadPortrait(self, ownerID, orderIfMissing = True):
        self.ownerLogoCont.Flush()
        if self.sr.node is None:
            return
        GetOwnerLogo(self.ownerLogoCont, ownerID, size=32, callback=True, orderIfMissing=orderIfMissing)

    def GetMenu(self):
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        multi = len(selected) > 1
        if multi:
            return
        node = self.sr.node
        ownerID = node.ownerInfo.ownerID
        ownerTypeID = node.ownerInfo.typeID
        m = GetMenuService().GetMenuFromItemIDTypeID(ownerID, ownerTypeID).filter(['UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'])
        warID = node.warID
        if warID:
            m += [[MenuLabel('UI/Corporations/Wars/OpenWarReport'), OpenWarReport, (warID,)]]
        return m

    def GetDragData(self, *args):
        node = self.sr.node
        data = KeyVal(__guid__='listentry.User', charID=node.ownerInfo.ownerID, info=node.ownerInfo)
        return [data]
