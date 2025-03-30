#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\recruitment\recruitmentEntry.py
from math import pi
import blue
import localization
import uthread
import utillib
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, Density
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveLabel, eveIcon
from eve.client.script.ui.services.corporation import corp_util as corputil
from eve.common.script.sys import idCheckers
from evecorporation import corp_ui_recruitment_const as rConst
from evecorporation.corp_ui_recruitment_const import MATCHED_COLOR, WHITE_COLOR, UNMATCHED_COLOR, SHOWSEARCHMATCH
from evecorporation.recruitment import get_recruitment_type, get_recruitment_group_name, get_recruitment_types_for_group_id
from evecorporation.recruitmentUtil import IsBitSetForTypeID, GetTimeZoneFromMask
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from globalConfig import IsContentComplianceControlSystemActive
from menu import MenuLabel

def HasAccess(corporationID):
    if corporationID != session.corpid:
        return False
    if const.corpRolePersonnelManager & session.corprole != const.corpRolePersonnelManager:
        return False
    return True


class RecruitmentEntry(SE_BaseClassCore):
    __guid__ = 'listentry.RecruitmentEntry'
    default_showHilite = False
    isDragObject = True
    LOGOSIZE = 48
    LOGOPADDING = LOGOSIZE * 2 + 18
    TEXTPADDING = 18
    CORPNAMEPAD = (LOGOPADDING,
     0,
     const.defaultPadding,
     0)
    CORPNAMECLASS = eveLabel.EveLabelLarge
    DESCPAD = (0,
     const.defaultPadding,
     const.defaultPadding * 2,
     16)
    DESCCLASS = eveLabel.EveLabelMedium
    DETAILSPAD = (TEXTPADDING,
     const.defaultPadding,
     const.defaultPadding,
     const.defaultPadding)
    DETAILSCLASS = eveLabel.EveLabelMedium
    RECRUITERSPAD = (0,
     const.defaultPadding,
     const.defaultPadding,
     const.defaultPadding)
    RECRUITERSCLASS = eveLabel.EveLabelMedium
    RECRCUITERSCONTAINERHEIGHT = 80
    COLUMNMARGIN = 10
    HEADERCONTAINER_HEIGHT = 54

    def Startup(self, *args):
        node = self.sr.node
        self.isDragObject = True
        self.corpSvc = sm.GetService('corp')
        self.headerContainer = Container(parent=self, align=uiconst.TOTOP, name='headerContainer', height=self.HEADERCONTAINER_HEIGHT, state=uiconst.UI_NORMAL)
        self.headerContainer.isDragObject = True
        self.headerContainer.GetDragData = self.GetDragData
        if not self.sr.node.standaloneMode:
            self.headerContainer.OnClick = self.ToggleExpanded
        self.headerContainer.OnMouseEnter = self.OnHeaderMouseEnter
        self.headerContainer.GetMenu = self.GetMenu
        self.rightCont = Container(parent=self.headerContainer, align=uiconst.TORIGHT, name='rightCont', width=0, state=uiconst.UI_PICKCHILDREN)
        if not self.sr.node.standaloneMode:
            self.expander = Sprite(parent=self.headerContainer, state=uiconst.UI_DISABLED, name='expander', pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Shared/getMenuIcon.png', align=uiconst.CENTERLEFT)
            if self.sr.node.expandedView:
                self.expander.rotation = -pi * 0.5
        self.corpLogo = eveIcon.GetLogoIcon(itemID=node.corporationID, parent=self.headerContainer, align=uiconst.CENTERLEFT, name='corpLogo', state=uiconst.UI_DISABLED, size=self.LOGOSIZE, ignoreSize=True, left=14, top=0)
        if node.allianceID:
            self.allianceLogo = Sprite(parent=self.headerContainer, align=uiconst.CENTERLEFT, name='allianceLogo', state=uiconst.UI_NORMAL, height=self.LOGOSIZE, width=self.LOGOSIZE, ignoreSize=True, left=self.LOGOSIZE + self.corpLogo.left, top=0)
            uthread.new(self.LoadAllianceLogo, self.allianceLogo, node.allianceID)
        else:
            self.allianceLogo = Sprite(parent=self.headerContainer, align=uiconst.CENTERLEFT, name='allianceLogo', state=uiconst.UI_NORMAL, pos=(self.LOGOSIZE + self.corpLogo.left,
             0,
             self.LOGOSIZE,
             self.LOGOSIZE), texturePath='res:/UI/Texture/defaultAlliance.dds')
            self.allianceLogo.opacity = 0.2
            self.allianceLogo.hint = localization.GetByLabel('UI/PeopleAndPlaces/OwnerNotInAnyAlliance', corpName=cfg.eveowners.Get(node.corporationID).ownerName)
        if not self.sr.node.standaloneMode:
            self.allianceLogo.OnClick = self.ToggleExpanded
        self.expiryLabel = eveLabel.EveLabelMedium(parent=self.rightCont, align=uiconst.TOPRIGHT, top=const.defaultPadding, left=const.defaultPadding)
        self.applyButton = Button(parent=self.rightCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/Apply'), align=uiconst.BOTTOMRIGHT, left=const.defaultPadding, top=const.defaultPadding, func=self.Apply, state=uiconst.UI_HIDDEN, opacity=0.0, density=Density.COMPACT)
        self.editButton = Button(parent=self.rightCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdEdit'), align=uiconst.BOTTOMRIGHT, left=const.defaultPadding, top=const.defaultPadding, func=self.EditRecruitmentAd, state=uiconst.UI_HIDDEN, density=Density.COMPACT)
        if IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
            self.editButton.Disable()
        self.removeButton = Button(parent=self.rightCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRemove'), align=uiconst.BOTTOMRIGHT, left=self.editButton.left + self.editButton.width + const.defaultPadding, top=const.defaultPadding, func=self.DeleteRecruitmentAd, state=uiconst.UI_HIDDEN, density=Density.COMPACT)
        self.warIcon = ButtonIcon(parent=self.rightCont, align=uiconst.TOPRIGHT, left=const.defaultPadding, top=const.defaultPadding, iconSize=20, width=24, height=24, texturePath='res:/UI/Texture/Icons/swords.png', func=self.OpenWarTab)
        self.warIcon.display = False
        self.gradeLabel = eveLabel.EveLabelLarge(parent=self.rightCont, name='grade', left=10, top=6, text='', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        self.gradeLabel.hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MatchHint')
        corpAndAllianceNameAndTitle = RecruitmentEntry.GetHeaderText(node.corporationID, node.adTitle)
        self.corpNameLabel = self.CORPNAMECLASS(parent=self.headerContainer, name='corpNameLabel', padding=self.CORPNAMEPAD, text=corpAndAllianceNameAndTitle, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        corpNameHeight = self.corpNameLabel.height + self.corpNameLabel.padTop + self.corpNameLabel.padBottom
        self.headerContainer.height = max(self.HEADERCONTAINER_HEIGHT, corpNameHeight)
        self.expandedParent = Container(parent=self)
        self.detailsContainer = GridContainer(name='detailsContainer', parent=self.expandedParent, align=uiconst.TOTOP, padding=(self.TEXTPADDING,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), lines=1, columns=2)
        Line(parent=self.expandedParent, align=uiconst.TOTOP, padTop=-5, color=(0.0, 0.0, 0.0, 0.15))
        self.descriptionContainer = ContainerAutoSize(parent=self.expandedParent, align=uiconst.TOTOP, padding=(self.TEXTPADDING,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.descriptionLabel = self.DESCCLASS(parent=self.descriptionContainer, name='descriptionLabel', align=uiconst.TOTOP, padding=self.DESCPAD, state=uiconst.UI_NORMAL)
        self.detailsContainerLeft = Container(parent=self.detailsContainer)
        self.detailsContainerRight = Container(parent=self.detailsContainer)
        self.expandedTextLabelLeft = self.DETAILSCLASS(parent=self.detailsContainerLeft, name='expandedTextLabel', align=uiconst.TOTOP, padRight=self.COLUMNMARGIN, state=uiconst.UI_NORMAL)
        self.expandedTextLabelLeft.OnSizeChanged = self.UpdateDetailsContainer
        self.expandedTextLabelRight = self.DETAILSCLASS(parent=self.detailsContainerRight, name='expandedTextLabelRight', align=uiconst.TOTOP, padLeft=self.COLUMNMARGIN, state=uiconst.UI_NORMAL)
        self.expandedTextLabelRight.OnSizeChanged = self.UpdateDetailsContainer
        self.recruitersContainer = Container(parent=self.expandedParent, name='recruitersContainer', align=uiconst.TOTOP, padding=self.DETAILSPAD, height=self.RECRCUITERSCONTAINERHEIGHT, state=uiconst.UI_HIDDEN)
        if not node.standaloneMode:
            Fill(bgParent=self.expandedParent, color=(0, 0, 0, 0.2))

    def LoadAllianceLogo(self, logo, ownerID, *args):
        sm.GetService('photo').GetAllianceLogo(ownerID, 128, logo, orderIfMissing=True)
        logo.hint = cfg.eveowners.Get(ownerID).ownerName

    def _OnSizeChange_NoBlock(self, newWidth, newHeight):
        if getattr(self, 'corpNameLabel', None):
            self.UpdateTextFade(duration=0)

    def UpdateDetailsContainer(self, *args):
        self.detailsContainer.height = max(self.expandedTextLabelLeft.textheight, self.expandedTextLabelRight.textheight)

    def Load(self, node):
        if node.fadeSize:
            toHeight, fromHeight = node.fadeSize
            self.clipChildren = True
            uicore.animations.MorphScalar(self, 'height', startVal=fromHeight, endVal=toHeight, duration=0.3)
            self.expandedParent.opacity = 0.0
            uicore.animations.FadeIn(self.expandedParent, duration=0.3)
        node.fadeSize = None
        if not node.standaloneMode:
            if not self.sr.node.expandedView and round(self.expander.rotation, 2) != 0.0:
                uicore.animations.Tr2DRotateTo(self.expander, -pi * 0.5, 0.0, duration=0.15)
            elif self.sr.node.expandedView and round(self.expander.rotation, 2) != round(-pi * 0.5, 2):
                uicore.animations.Tr2DRotateTo(self.expander, 0.0, -pi * 0.5, duration=0.15)
        if node.corpView:
            expireTime = node.advert.expiryDateTime - blue.os.GetWallclockTime()
            if expireTime > 0:
                expirationString = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdExpiresIn', adDuration=expireTime)
            else:
                expirationString = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdExpired')
            expiryLabel = self.expiryLabel
            expiryLabel.text = expirationString
            if expireTime < const.DAY:
                expiryLabel.color = Color.RED
            self.SetRightContWidth(isCorpView=True)
        else:
            if node.grade is not None:
                self.gradeLabel.text = localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=node.grade)
            if len(getattr(node, 'warOpponents', set())) > 0:
                allWarsTextList = []
                for corpAtWar in node.warOpponents:
                    allWarsTextList.append(cfg.eveowners.Get(corpAtWar).name)

                allWarsText = '<br>'.join(allWarsTextList)
                warText = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorpAtWarWith', warTargets=allWarsText)
                self.warIcon.hint = warText
                self.warIcon.display = True
                self.warIcon.left = self.gradeLabel.textwidth + self.gradeLabel.left + 6
            else:
                self.warIcon.display = False
            self.SetRightContWidth(isCorpView=False)
        if node.expandedView:
            self.expandedParent.display = True
            self.descriptionLabel.text = node.advert.description.strip()
            leftText = RecruitmentEntry.GetLeftColumnText(node)
            self.expandedTextLabelLeft.text = leftText
            rightText = RecruitmentEntry.GetRightColumnText(node)
            self.expandedTextLabelRight.text = rightText
            self.detailsContainer.height = max(self.expandedTextLabelLeft.textheight, self.expandedTextLabelRight.textheight)
            self.LoadRecruiters()
        else:
            self.expandedParent.display = False

    def LoadRecruiters(self):
        node = self.sr.node
        if not node.recruiters:
            return
        if len(self.recruitersContainer.children):
            return
        self.recruitersContainer.Flush()
        self.recruitersContainer.display = True
        recruitersLabel = self.RECRUITERSCLASS(parent=self.recruitersContainer, name='recruitersLabel', align=uiconst.TOTOP, bold=True, padding=self.RECRUITERSPAD, text=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRecruiters'))
        numRecruiters = len(node.recruiters)
        lines = numRecruiters / 3
        if numRecruiters % 3:
            lines += 1
        if numRecruiters < 3:
            columns = numRecruiters
        else:
            columns = 3
        top = recruitersLabel.textheight + recruitersLabel.padTop + recruitersLabel.padBottom
        self.recruitersContainer.height = top + self.RECRCUITERSCONTAINERHEIGHT
        self.recuitersGrid = GridContainer(parent=self.recruitersContainer, align=uiconst.TOTOP, lines=lines, columns=columns, height=lines * 32 + 4)
        menuSvc = GetMenuService()
        for recruiterID in node.recruiters:
            self._LoadRecruiterToGrid(menuSvc, node, recruiterID)

    def _LoadRecruiterToGrid(self, menuSvc, node, recruiterID):
        recruiterUserObject = cfg.eveowners.Get(recruiterID)
        recruiterTypeID = recruiterUserObject.typeID
        container = Container(parent=self.recuitersGrid, clipChildren=True, padding=(const.defaultPadding,
         2,
         const.defaultPadding,
         2))
        eveIcon.GetOwnerLogo(container, recruiterID, size=32, orderIfMissing=True)
        startInfoTag = '<url=showinfo:%d//%d>' % (recruiterTypeID, recruiterID)
        recruiterLink = localization.GetByLabel('UI/Agents/InfoLink', startInfoTag=startInfoTag, startColorTag='<color=-2039584>', objectName=recruiterUserObject.name, endColorTag='</color>', endnfoTag='</url>')
        isRecruiting = (utillib.KeyVal(recruiterID=recruiterID, corporationID=node.corporationID, adID=node.advert.adID),)
        m = []
        m += menuSvc.GetMenuFromItemIDTypeID(recruiterID, recruiterTypeID, isRecruiting=isRecruiting)
        m += menuSvc.GetGMTypeMenu(recruiterTypeID, divs=True)
        eveLabel.EveLabelMedium(parent=container, name='nameLabel', text=recruiterLink, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, left=36, GetMenu=lambda : m)

    @staticmethod
    def GetLeftColumnText(node):
        text = ''
        playStyles = []
        otherOptions = []
        optionsTextList = []
        advertMask = node.advert.typeMask or 0
        otherMask = node.advert.otherMask or 0
        if node.searchMask is None and node.otherMask is None:
            showSearchMatch = False
        else:
            showSearchMatch = True
        if showSearchMatch:
            memberText = localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/CorporationMemberCount', memberCount=node.memberCount)
            text += MATCHED_COLOR + memberText + '<br><br>'
        for combinedGroupID in rConst.PLAYSTYLE_GROUPS:
            if combinedGroupID not in rConst.COMBINED_GROUPS:
                continue
            adTypeIDs = rConst.COMBINED_GROUPS[combinedGroupID].playstyleTypeIDs
            for adTypeID in adTypeIDs:
                adType = get_recruitment_type(adTypeID)
                if advertMask & adType.typeMask:
                    playStyles.append(adType)

        if playStyles:
            optionsTextList = [ RecruitmentEntry.ColorIfSearchMatch(adType, node.searchMask, showSearchMatch) for adType in playStyles ]
        otherPlaystyles = (rConst.NEWPILOTFRIENTLY_TYPEID, rConst.NEWPILOTFOCUSED_TYPEID, rConst.ROLEPLAY_TYPEID)
        for adTypeID in otherPlaystyles:
            if IsBitSetForTypeID(adTypeID, otherMask):
                adType = get_recruitment_type(adTypeID)
                otherOptions.append(adType)

        if otherOptions:
            optionsTextList += [ RecruitmentEntry.ColorIfSearchMatch(adType, node.otherMask, showSearchMatch) for adType in otherOptions ]
        if optionsTextList:
            optionsText = ', '.join(optionsTextList)
            text += '<b>%s%s</b><br>%s' % (WHITE_COLOR, get_recruitment_group_name(rConst.PLAYSTYLE_GROUPID), optionsText) + '<br><br>'
        minSPtext = FmtAmt(node.minSP)
        text += '<b>%s%s</b><br>%s%s<br><br>' % (WHITE_COLOR,
         localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/MinimumSPrequirement'),
         MATCHED_COLOR,
         minSPtext)
        statusText = node.friendlyFireStatus
        text += '<b>%s%s</b><br>%s%s' % (WHITE_COLOR,
         localization.GetByLabel('UI/Corporations/CorpUIHome/FriendlyFire'),
         MATCHED_COLOR,
         statusText)
        return text

    @staticmethod
    def ColorIfSearchMatch(adType, searchMask, showSearchMatch):
        if showSearchMatch:
            if adType.typeMask & searchMask:
                typeName = adType.typeName
                return MATCHED_COLOR + typeName
            else:
                return UNMATCHED_COLOR + adType.typeName
        return MATCHED_COLOR + adType.typeName

    @staticmethod
    def GetRightColumnText(node):
        text = ''
        advertMask = node.advert.typeMask
        langMask = node.advert.langMask
        if node.searchMask is None and node.otherMask is None:
            showSearchMatch = False
        else:
            showSearchMatch = True
        hint = []
        for adType in get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID):
            if adType.typeMask & advertMask:
                hint.append(RecruitmentEntry.ColorIfSearchMatch(adType, node.searchMask, showSearchMatch))

        if hint:
            hint = ', '.join(hint)
            text += '<b>%s%s</b><br>%s<br><br>' % (WHITE_COLOR, get_recruitment_group_name(rConst.AREA_OF_OPERATIONS_GROUPID), hint)
        typeList = []
        for adType in get_recruitment_types_for_group_id(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE):
            if langMask and langMask & adType.typeMask:
                typeList.append((adType.typeName.lower(), adType))

        if typeList:
            typeList = SortListOfTuples(typeList)
            typeList = ', '.join((RecruitmentEntry.ColorIfSearchMatch(adType, node.searchLangMask, showSearchMatch) for adType in typeList))
            text += '<b>%s%s</b><br>%s<br><br>' % (WHITE_COLOR, get_recruitment_group_name(corputil.RECRUITMENT_GROUP_PRIMARY_LANGUAGE), typeList)
        fromProportion, toProportion = settings.char.ui.Get('corp_recruitment_searchTimeZoneRange', (0.0, 1.0))
        if node.timeZoneMask1 is None:
            f1, t1 = (0, 24)
        else:
            f1, t1 = GetTimeZoneFromMask(node.timeZoneMask1)
        fromHour = int(fromProportion * 24)
        toHour = int(toProportion * 24)
        color = MATCHED_COLOR
        if showSearchMatch:
            if (fromHour <= f1 and toHour >= t1 or f1 < fromHour < t1 or f1 < toHour < t1) and SHOWSEARCHMATCH and node.searchMask is not None:
                color = MATCHED_COLOR
            else:
                color = UNMATCHED_COLOR
        text += color + localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/TimeZoneToAndFrom2', startTime=f1 * const.HOUR, endTime=t1 * const.HOUR, timeZoneText=localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/TimeZone1'))
        return text

    def OpenWarTab(self, *args):
        uthread.new(self.OpenWarTabThread)

    def OpenWarTabThread(self, *args):
        node = self.sr.node
        if node.allianceID:
            typeID = const.typeAlliance
            itemID = node.allianceID
        else:
            typeID = const.typeCorporation
            itemID = node.corporationID
        infoWnd = sm.GetService('info').ShowInfo(typeID, itemID)
        if infoWnd:
            counter = 0
            while getattr(infoWnd, 'maintabs', None) is None and counter < 5:
                blue.pyos.synchro.SleepWallclock(100)
                counter += 1

            if getattr(infoWnd, 'maintabs', None):
                infoWnd.maintabs.ShowPanelByName(localization.GetByLabel('UI/InfoWindow/TabNames/WarHistory'))

    @staticmethod
    def GetDynamicHeight(node, width):
        cls = RecruitmentEntry
        corpAndAllianceNameAndTitle = RecruitmentEntry.GetHeaderText(node.corporationID, node.adTitle)
        pl, pt, pr, pb = cls.CORPNAMEPAD
        corpNameWidth, corpNameHeight = cls.CORPNAMECLASS.MeasureTextSize(corpAndAllianceNameAndTitle)
        corpNameHeight += pt + pb
        baseHeight = max(cls.HEADERCONTAINER_HEIGHT, corpNameHeight)
        if not node.expandedView:
            return baseHeight
        pl, pt, pr, pb = cls.DESCPAD
        descWidth, descHeight = cls.DESCCLASS.MeasureTextSize(node.advert.description, width=width - pl - pr)
        descHeight += pt + pb
        pl, pt, pr, pb = cls.DETAILSPAD
        leftText = RecruitmentEntry.GetLeftColumnText(node)
        leftWidth, leftHeight = cls.DETAILSCLASS.MeasureTextSize(leftText, width=(width - pl - pr) / 2 - cls.COLUMNMARGIN)
        leftHeight += pt + pb
        rightText = RecruitmentEntry.GetRightColumnText(node)
        rightWidth, rightHeight = cls.DETAILSCLASS.MeasureTextSize(rightText, width=(width - pl - pr) / 2 - cls.COLUMNMARGIN)
        rightHeight += pt + pb
        recruitersHeight = 0
        if node.recruiters:
            pl, pt, pr, pb = cls.RECRUITERSPAD
            recruitHeaderWidth, recruitHeaderHeight = cls.RECRUITERSCLASS.MeasureTextSize(localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/AdRecruiters'), width=width - pl - pr, bold=1)
            recruitersHeight = cls.RECRCUITERSCONTAINERHEIGHT + recruitHeaderHeight + pt + pb
        return baseHeight + descHeight + max(leftHeight, rightHeight) + recruitersHeight + 8

    @staticmethod
    def GetHeaderText(corpID, adTitle):
        headerText = '<b>%s</b>' % cfg.eveowners.Get(corpID).ownerName
        headerText += '<br>%s' % adTitle
        return headerText

    def GetMenu(self):
        node = self.sr.node
        m = []
        if node.corpView:
            if HasAccess(self.sr.node.corporationID):
                if not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                    m.append((MenuLabel('UI/Corporations/CorporationWindow/Recruitment/AdEdit'), self.EditRecruitmentAd))
                m.append((MenuLabel('UI/Corporations/CorporationWindow/Recruitment/AdRemove'), self.DeleteRecruitmentAd))
        elif self.sr.node.corporationID != session.corpid:
            m.append((MenuLabel('UI/Corporations/CorporationWindow/Recruitment/ApplyToJoinCorporation'), self.Apply))
        if not self.sr.node.standaloneMode:
            m.append((MenuLabel('UI/Corporations/CorporationWindow/Recruitment/OpenAdInNewWindow'), sm.GetService('corp').OpenCorpAdInNewWindow, (node.advert.corporationID, node.advert.adID)))
        m.append(None)
        if node.advert:
            if idCheckers.IsCorporation(node.corporationID):
                m += [(MenuLabel('UI/Common/Corporation'), GetMenuService().GetMenuFromItemIDTypeID(node.corporationID, const.typeCorporation))]
            if idCheckers.IsAlliance(node.allianceID):
                m += [(MenuLabel('UI/Common/Alliance'), GetMenuService().GetMenuFromItemIDTypeID(node.allianceID, const.typeAlliance))]
            if m:
                m += [None]
        if node.Get('GetMenu', None):
            m += node.GetMenu(self)
        return m

    def ToggleExpanded(self):
        reloadNodes = [self.sr.node]
        if self.sr.node.expandedView:
            PlaySound(uiconst.SOUND_COLLAPSE)
            uicore.animations.Tr2DRotateTo(self.expander, -pi * 0.5, 0.0, duration=0.15)
            self.sr.node.expandedView = False
            current = settings.char.ui.Get('corporation_recruitmentad_expanded', {})
            current[self.sr.node.corpView] = None
            settings.char.ui.Set('corporation_recruitmentad_expanded', current)
        else:
            PlaySound(uiconst.SOUND_EXPAND)
            for each in self.sr.node.scroll.sr.nodes:
                if each.expandedView:
                    reloadNodes.append(each)
                    each.expandedView = False

            uicore.animations.Tr2DRotateTo(self.expander, 0.0, -pi * 0.5, duration=0.15)
            current = settings.char.ui.Get('corporation_recruitmentad_expanded', {})
            current[self.sr.node.corpView] = self.sr.node.advert.adID
            settings.char.ui.Set('corporation_recruitmentad_expanded', current)
            if self.sr.node.recruiters is None:
                self.sr.node.recruiters = self.corpSvc.GetRecruiters(self.sr.node.advert.adID)
            self.sr.node.expandedView = True
            self.sr.node.fadeSize = (RecruitmentEntry.GetDynamicHeight(self.sr.node, self.width), self.height)
        self.sr.node.scroll.ReloadNodes(reloadNodes, updateHeight=True)

    def Apply(self, *args):
        applicationID = self.corpSvc.ApplyForMembership(self.sr.node.corporationID)
        with ExceptionEater('eventLog'):
            self.corpSvc.LogCorpRecruitmentEvent(['corporationID',
             'allianceID',
             'applyingCorporationID',
             'adID',
             'applicationID'], 'ApplyToJoin', session.corpid, session.allianceid, self.sr.node.corporationID, self.sr.node.advert.adID, applicationID)

    def DeleteRecruitmentAd(self, *args):
        if eve.Message('CorpAdsAreYouSureYouWantToDelete', None, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            self.corpSvc.DeleteRecruitmentAd(self.sr.node.advert.adID)

    def EditRecruitmentAd(self, *args):
        self.sr.node.editFunc(self.sr.node.advert)

    def OnHeaderMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        if self.sr.node.standaloneMode:
            return
        self.ShowHilite()
        self.ShowButtons()
        self.hiliteTimer = timerstuff.AutoTimer(1, self._CheckIfStillHilited)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        if self.sr.node.standaloneMode:
            return
        self.ShowButtons()
        self.hiliteTimer = timerstuff.AutoTimer(1, self._CheckIfStillHilited)

    def OnMouseExit(self, *args):
        pass

    def _CheckIfStillHilited(self):
        if self.sr.node.standaloneMode:
            return
        if uicore.uilib.mouseOver.IsUnder(self) or uicore.uilib.mouseOver is self:
            return
        self.HideHilite()
        self.hiliteTimer = None
        for each in (self.applyButton, self.editButton, self.removeButton):
            if each.display:
                uicore.animations.FadeTo(each, each.opacity, 0.0, duration=0.1, callback=self.HideButtons)

    def SetRightContWidth(self, isCorpView = False):
        if isCorpView:
            width = self.expiryLabel.textwidth + self.expiryLabel.left
            if self.removeButton.display:
                width = max(width, self.removeButton.left + self.removeButton.width)
        else:
            width = self.gradeLabel.textwidth + 10
            if self.warIcon.display:
                width += self.warIcon.width
            if self.applyButton.display:
                width = max(width, self.applyButton.width + self.applyButton.left)
        self.rightCont.width = width

    def HideButtons(self):
        for each in (self.applyButton, self.editButton, self.removeButton):
            each.display = False

        self.UpdateTextFade()

    def ShowButtons(self):
        if self.sr.node.corpView:
            self.applyButton.display = False
            if HasAccess(self.sr.node.corporationID):
                self.editButton.display = True
                uicore.animations.FadeTo(self.editButton, self.editButton.opacity, 1.0, duration=0.3)
                self.removeButton.display = True
                uicore.animations.FadeTo(self.removeButton, self.removeButton.opacity, 1.0, duration=0.3)
        else:
            if self.sr.node.corporationID != session.corpid:
                self.applyButton.display = True
            uicore.animations.FadeTo(self.applyButton, self.applyButton.opacity, 1.0, duration=0.3)
            self.editButton.display = False
            self.removeButton.display = False
        self.UpdateTextFade()

    def UpdateTextFade(self, duration = 0.3):
        self.SetRightContWidth(isCorpView=self.sr.node.corpView)
        if self.sr.node.corpView:
            rightPad = self.rightCont.width
        elif self.applyButton.display:
            rightPad = self.rightCont.width
        else:
            rightPad = self.rightCont.width
        fadeEnd = self.width - rightPad - self.corpNameLabel.padLeft - 10
        self.corpNameLabel.SetRightAlphaFade(fadeEnd=fadeEnd, maxFadeWidth=20)

    def GetDragData(self, *args):
        return [self.sr.node]
