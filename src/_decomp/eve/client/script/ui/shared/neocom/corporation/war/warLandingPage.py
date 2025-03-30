#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warLandingPage.py
import gametime
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import Align
from carbonui.button.group import ButtonGroup
from carbonui.control.scrollContainer import ScrollContainer
import eve.common.lib.appConst as appConst
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.neocom.corporation.war.landingPageCont import LandingPageCont
from eveservices.menu import GetMenuService
from evewar.util import IsWarInHostileState, IsWarInSpoolup, IsWarFinished
from localization import GetByLabel
from utillib import KeyVal
from eve.common.script.sys.idCheckers import IsNPCCorporation
import blue

class WarLandingPage(Container):
    default_name = 'warLandingPage'

    def __init__(self, *args, **kwargs):
        super(WarLandingPage, self).__init__(*args, **kwargs)
        self.warCont = None
        self.billsCont = None
        self.alliesCont = None
        self.mutualWarsCont = None
        self.eligibilityCont = None
        self.peaceCont = None

    def Load(self, *args):
        self.LoadPage()

    def LoadPage(self):
        self.Flush()
        declareBtnGroup = ButtonGroup(parent=self, align=Align.TOBOTTOM, padTop=8)
        declareBtnGroup.AddButton(GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'), self.OnDeclareWarBtn)
        self.scroll_cont = ScrollContainer(parent=self)
        self.warCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPageWarsHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPageWarsDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPageWarsTooltip'), padTop=4)
        self.billsCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPageWarBillsHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPageWarBillsDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPageWarBillsTooltip'))
        self.alliesCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPageAlliesHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPageAlliesDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPageAlliesTooltip'))
        self.mutualWarsCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPageMutualWarsHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPageMutualWarsDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPageMutualWarsTooltip'))
        self.eligibilityCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPageWarEligibilityHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPageWarEligibilityDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPageWarEligibilityTooltip'))
        self.peaceCont = LandingPageCont(parent=self.scroll_cont, headerText=GetByLabel('UI/Corporations/Wars/LandingPagePeaceHeader'), text=GetByLabel('UI/Corporations/Wars/LandingPagePeaceDesc'), tooltipText=GetByLabel('UI/Corporations/Wars/LandingPagePeaceTooltip'))
        uthread.new(self.UpdateStatus)

    def OnDeclareWarBtn(self, *args):
        GetMenuService().DeclareWar()

    def UpdateStatus(self):
        info = self.GetLandingPageInfo()
        self.warCont.UpdateCurrentStatus(self.GetCurrentWarStatus(info))
        self.billsCont.UpdateCurrentStatus(self.GetCurrentWarBillStatus(info))
        self.alliesCont.UpdateCurrentStatus(self.GetCurrentAlliesStatus(info))
        self.mutualWarsCont.UpdateCurrentStatus(self.GetCurrentMutualWarStatus(info))
        self.eligibilityCont.UpdateCurrentStatus(self.GetCurrentWarEligibility(info))
        self.peaceCont.UpdateCurrentStatus(self.GetCurrentPeaceTimeInfo(info))

    def GetCurrentWarStatus(self, info):
        if info.currentWars:
            if info.pendingWars:
                labelPath = 'UI/Corporations/Wars/LandingPageWarStatusCurrentAndPendingWars'
            else:
                labelPath = 'UI/Corporations/Wars/LandingPageWarStatusCurrentWars'
        elif info.pendingWars:
            labelPath = 'UI/Corporations/Wars/LandingPageWarStatusPendingWars'
        else:
            labelPath = 'UI/Corporations/Wars/LandingPageWarStatusNoWars'
        return GetByLabel(labelPath, corpOrAllianceLink=info.corpOrAllianceLink, numActiveWars=info.currentWars, numPendingWars=info.pendingWars)

    def GetCurrentWarBillStatus(self, info):
        unpaidWarBills = info.unpaidWarBills
        if unpaidWarBills is None:
            return ''
        if unpaidWarBills:
            text = GetByLabel('UI/Corporations/Wars/LandingPageWarBillStatusWithBills', numBills=unpaidWarBills)
        else:
            text = GetByLabel('UI/Corporations/Wars/LandingPageWarBillStatusWithoutBills')
        text += ' <url=localsvc:method=ShowPayableCorpBills>%s</url>' % GetByLabel('UI/Corporations/Wars/ViewBills')
        return text

    def GetCurrentAlliesStatus(self, info):
        if info.numAllyWars:
            if info.numAllies:
                labelPath = 'UI/Corporations/Wars/LandingPagAllyStatusAllyAndAllied'
            else:
                labelPath = 'UI/Corporations/Wars/LandingPagAllyStatusAlly'
        elif info.numAllies:
            labelPath = 'UI/Corporations/Wars/LandingPagAllyStatusAllied'
        else:
            labelPath = 'UI/Corporations/Wars/LandingPagAllyStatusNoAllies'
        return GetByLabel(labelPath, corpOrAllianceLink=info.corpOrAllianceLink, numAllyWars=info.numAllyWars, numAllies=info.numAllies)

    def GetCurrentMutualWarStatus(self, info):
        if info.nonFinishedMutualWars:
            labelPath = 'UI/Corporations/Wars/LandingPageMutualWarsExist'
        else:
            labelPath = 'UI/Corporations/Wars/LandingPageMutualWarsNoWar'
        return GetByLabel(labelPath, corpOrAllianceLink=info.corpOrAllianceLink, numMutualWars=info.nonFinishedMutualWars)

    def GetCurrentWarEligibility(self, info):
        if info.warPermit:
            if info.validWarHQs:
                labelPath = 'UI/Corporations/Wars/LandingPageEligibilityStatusWarPermitAndWarHq'
            else:
                labelPath = 'UI/Corporations/Wars/LandingPageEligibilityStatusWarPermitAndNoHq'
        else:
            labelPath = 'UI/Corporations/Wars/LandingPageEligibilityStatusNoPermit'
        return GetByLabel(labelPath, corpOrAllianceLink=info.corpOrAllianceLink, numHq=info.validWarHQs)

    def GetCurrentPeaceTimeInfo(self, info):
        numWarTreaties = info.numWarTreaties
        if numWarTreaties:
            labelPath = 'UI/Corporations/Wars/LandingPageForcedPeaceTreaties'
        else:
            labelPath = 'UI/Corporations/Wars/LandingPageNoForcedPeace'
        return GetByLabel(labelPath, corpOrAllianceLink=info.corpOrAllianceLink, numWarTreaties=numWarTreaties)

    def GetLandingPageInfo(self):
        warPermit = not sm.GetService('warPermit').DoesMyCorpHaveNegativeWarPermit()
        ourWars, unpaidWarBills, validWarHQs, numPeaceTreaties = uthread.parallel([(self.GetAllOurWars, ()),
         (self.GetUnpaidWarBills, ()),
         (self.GetValidWarHQs, (warPermit,)),
         (self.GetNumPeaceTreatyOwners, ())])
        now = gametime.GetWallclockTime()
        numFacWars = len(sm.GetService('facwar').GetFactionWars(session.corpid).values())
        currentWars = len([ x for x in ourWars.itervalues() if IsWarInHostileState(x, now) ])
        currentWars += numFacWars
        pendingWars = len([ x for x in ourWars.itervalues() if IsWarInSpoolup(x) ])
        nonFinishedMutualWars = len([ x for x in ourWars.itervalues() if not IsWarFinished(x) and x.mutual ])
        nonFinishedMutualWars += numFacWars
        numAllyWars, numAllies = self.GetAllyWarsAndAllies(ourWars)
        return KeyVal(corpOrAllianceLink=self.GetCorpOrAllianceLink(), currentWars=currentWars, pendingWars=pendingWars, unpaidWarBills=unpaidWarBills, numAllyWars=numAllyWars, numAllies=numAllies, nonFinishedMutualWars=nonFinishedMutualWars, warPermit=warPermit, validWarHQs=validWarHQs, numWarTreaties=numPeaceTreaties)

    def GetValidWarHQs(self, warPermit):
        if IsNPCCorporation(session.corpid) or not warPermit:
            return 0
        return len(sm.GetService('structureDirectory').GetValidWarHQs())

    def GetAllOurWars(self):
        corpOrAllianceID = session.allianceid or session.corpid
        allWars = sm.GetService('war').GetWars(corpOrAllianceID)
        return allWars

    def GetNumPeaceTreatyOwners(self):
        if IsNPCCorporation(session.corpid):
            return 0
        outgoingTreaties, incomingTreaties = sm.GetService('war').GetPeaceTreaties()
        ownerIDs = {treaty.otherOwnerID for treaty in outgoingTreaties + incomingTreaties}
        return len(ownerIDs)

    def GetCorpOrAllianceLink(self):
        corpOrAllianceID = session.allianceid or session.corpid
        corpOrAllianceInfo = cfg.eveowners.Get(corpOrAllianceID)
        corpOrAllianceLink = GetShowInfoLink(corpOrAllianceInfo.typeID, corpOrAllianceInfo.ownerName, corpOrAllianceID)
        return corpOrAllianceLink

    def GetUnpaidWarBills(self):
        if (const.corpRoleAccountant | const.corpRoleJuniorAccountant) & session.corprole == 0:
            return None
        if session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID != session.corpid:
            return None
        ourWars = self.GetAllOurWars()
        if not ourWars:
            return None
        if session.allianceid:
            bills = sm.GetService('alliance').GetBills()
        else:
            bills = sm.RemoteSvc('billMgr').GetCorporationBills()
        unpaidWarBills = len([ x for x in bills if x.billTypeID == appConst.billTypeWarBill and not x.paid ])
        return unpaidWarBills

    def GetAllyWarsAndAllies(self, ourWars):
        corpOrAllianceID = session.allianceid or session.corpid
        numAllyWars = len([ x for x in ourWars.itervalues() if corpOrAllianceID in x.allies ])
        allies = set()
        for eachWar in ourWars.itervalues():
            if corpOrAllianceID in (eachWar.declaredByID, eachWar.againstID):
                allies.update(eachWar.allies.keys())

        numAllies = len(allies)
        return (numAllyWars, numAllies)

    def Copy(self, *args):
        textList = []
        for each in [self.warCont,
         self.billsCont,
         self.alliesCont,
         self.mutualWarsCont,
         self.eligibilityCont,
         self.peaceCont]:
            if not each or each.destroyed:
                continue
            text = each.GetAllContText()
            textList.append(text)

        allText = '\n\n'.join(textList)
        allText = allText.replace('<t>', '\t')
        strippedText = StripTags(allText)
        if strippedText:
            blue.pyos.SetClipboardData(strippedText)
