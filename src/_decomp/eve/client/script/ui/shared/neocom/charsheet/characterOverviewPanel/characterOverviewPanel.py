#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\characterOverviewPanel\characterOverviewPanel.py
import eveformat.client
import expertSystems.client
import localization
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextColor, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from characterdata.ancestries import get_ancestry_name
from characterdata.bloodlines import get_bloodline_name
from characterdata.races import get_race_name
from characterdata.schools import get_school_name
from eve.client.script.ui.control.eveIcon import LogoIcon, GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveCaptionSmall
from eve.client.script.ui.shared.cloneGrade import ORIGIN_CHARACTERSHEET
from eve.client.script.ui.shared.cloneGrade.cloneStateIcon import CloneStateIcon
from eve.client.script.ui.shared.neocom.avatarHeaderPreview import AvatarHeaderPreview
from eve.common.lib import appConst
from eve.common.lib import appConst as const
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from localization import GetByLabel
from playerprogression.ui.totalnetworthcontainer import TotalNetWorthProgressionContainer
from eve.client.script.ui.shared.neocom.charsheet.characterOverviewPanel.characterOverviewElements import AtWarIconAndLabel, CHAR_INFO_ELEMENT_HEIGHT, CharacterInfoElement, CharacterInfoHomeStation, CharacterInfoSecurityStatus, EmpireIcon, IconButtonCont
RIGHT_SIDE_PADDING = 22
LEFT_SIDE_PADDING = 32
BOTTOM_ICONS_PADDING = 22
BOTTOM_CONT_HEIGHT = 250

class CharacterSheetCharacterOverviewPanel(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.charMgr = sm.RemoteSvc('charMgr')
        self.charsvc = sm.GetService('cc')
        charinfo = self.charMgr.GetPublicInfo(session.charid)
        self.uiCont = Container(parent=self, name='uiCont', align=uiconst.TOALL)
        self.topCont = Container(parent=self.uiCont, name='topCont', align=uiconst.TOTOP_NOPUSH, height=200)
        self.ConstructTopCont(charinfo)
        self.bottomCont = Container(parent=self.uiCont, name='bottomCont', align=uiconst.TOBOTTOM_NOPUSH, height=BOTTOM_CONT_HEIGHT)
        self.ConstructBottomCont(charinfo)
        self.centralCont = Container(parent=self.uiCont, name='centralCont', align=uiconst.TOBOTTOM_PROP, height=0.5, alignMode=uiconst.TOTOP, width=1.0)
        self.ConstructCentralCont(attributes['toggleFunc'])
        self.ConstructAvatarPreview()
        self.UpdateToggleButton(attributes['isCharsheetExpanded'], animate=False)

    def ConstructTopCont(self, charinfo):
        self.windowNameCont = ContainerAutoSize(name='windowNameCont', parent=self.topCont, align=uiconst.TOPLEFT, minHeight=25, left=16, top=16)
        EveCaptionSmall(parent=self.windowNameCont, text=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterSheetCaption'), align=uiconst.CENTERLEFT, padding=(12, 0, 40, 0), color=TextColor.HIGHLIGHT)
        iconsCont = ContainerAutoSize(parent=self.topCont, name='iconsCont', align=uiconst.TOPRIGHT, width=64, top=50, left=18)
        EmpireIcon(parent=iconsCont, name='empireIcon', align=uiconst.TOTOP, empireID=session.raceID, width=64, height=64)
        if sm.GetService('war').IsPlayerCurrentlyAtWarOrInFW():
            AtWarIconAndLabel(parent=iconsCont, align=uiconst.TOTOP, height=AtWarIconAndLabel.iconSize)

    def SetExpanded(self, animate = False):
        self.UpdateToggleButton(expanded=True, animate=animate)
        if animate:
            animations.FadeTo(self.windowNameCont, self.windowNameCont.opacity, 0.0, duration=0.4)
        else:
            self.windowNameCont.opacity = 0.0

    def SetNotExpanded(self, animate = False):
        self.UpdateToggleButton(expanded=False, animate=animate)
        if animate:
            animations.FadeTo(self.windowNameCont, self.windowNameCont.opacity, 1.0, duration=0.4)
        else:
            self.windowNameCont.opacity = 1.0

    def GetRaceIconHint(self, charinfo):
        if charinfo.ancestryID == appConst.ancestryUndefined:
            charBackgroundInfo = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundInformationNoAncestry', raceName=get_race_name(charinfo.raceID), bloodlineName=get_bloodline_name(charinfo.bloodlineID), schoolName=get_school_name(charinfo.schoolID))
        else:
            charBackgroundInfo = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundInformation', raceName=get_race_name(charinfo.raceID), bloodlineName=get_bloodline_name(charinfo.bloodlineID), ancestryName=get_ancestry_name(charinfo.ancestryID), schoolName=get_school_name(charinfo.schoolID))
        return charBackgroundInfo

    def ConstructToggleBtn(self, container, toggleFunc):
        self.toggleBtn = Button(parent=container, name='toggleBtn', align=uiconst.CENTERLEFT, iconSize=16, texturePath='res:/UI/Texture/Shared/DarkStyle/forward.png', func=toggleFunc, uniqueUiName=pConst.UNIQUE_NAME_EXPAND_CHARSHEET)

    def UpdateToggleButton(self, expanded, animate = True):
        if expanded:
            self.toggleBtn.texturePath = 'res:/UI/Texture/Shared/DarkStyle/backward.png'
        else:
            self.toggleBtn.texturePath = 'res:/UI/Texture/Shared/DarkStyle/forward.png'

    def ConstructCharacterInfo(self, charinfo):
        self.ConstructCharacterInfoName(self.charInfoCont)
        self.ConstructCharacterInfoBirthDate(charinfo, self.charInfoCont)
        self.ConstructCharacterInfoTotalNetWorth(self.charInfoCont)
        self.ConstructCharacterInfoSecurityStatus(self.charInfoCont)
        self.ConstructCharacterInfoHomeStation(self.charInfoCont)
        self.ConstructCharacterTotalSkillPoints(self.charInfoCont)

    @staticmethod
    def ConstructCharacterInfoName(container):
        characterName = cfg.eveowners.Get(session.charid).name
        characterLink = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=characterName, info=('showinfo', const.typeCharacter, session.charid))
        EveCaptionLarge(text=characterLink, parent=container, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padBottom=2)

    @staticmethod
    def ConstructCharacterInfoBirthDate(charinfo, container):
        birthDate = localization.formatters.FormatDateTime(value=charinfo.createDateTime, dateFormat='short', timeFormat='short')
        CharacterInfoElement(parent=container, name='birthdateCont', align=uiconst.TOTOP, height=CHAR_INFO_ELEMENT_HEIGHT, titleText=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BornTitle'), valueText=birthDate)

    @staticmethod
    def ConstructCharacterInfoTotalNetWorth(container):
        TotalNetWorthProgressionContainer(parent=container, name='totalNetWorthCont', align=uiconst.TOTOP, height=CHAR_INFO_ELEMENT_HEIGHT)

    @staticmethod
    def ConstructCharacterInfoSecurityStatus(container):
        securityStatus = sm.GetService('crimewatchSvc').GetMySecurityStatus()
        roundedSecurityStatus = localization.formatters.FormatNumeric(securityStatus, decimalPlaces=1)
        roundedSecurityStatus = roundedSecurityStatus.replace(',', '.')
        whereAttacked = sm.GetService('crimewatchSvc').GetSecurityWhereAttacked()
        secStatusTextList = [GetByLabel('UI/AgentFinder/SecurityStatus')]
        if whereAttacked:
            securityStatusText = eveformat.security_status(whereAttacked)
            if whereAttacked == 1.0:
                secStatusTextList += [GetByLabel('UI/CharacterSheet/CharacterSheetWindow/AttackedByEmpireFactionPolice2', securityStatus=securityStatusText)]
            else:
                secStatusTextList += [GetByLabel('UI/CharacterSheet/CharacterSheetWindow/AttackedByEmpireFactionPolice', securityStatus=securityStatusText)]
        secStatusTooltip = '<br>'.join(secStatusTextList)
        CharacterInfoSecurityStatus(parent=container, name='securityStatusCont', align=uiconst.TOTOP, height=CHAR_INFO_ELEMENT_HEIGHT, titleText=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusTitle'), valueText='%s' % roundedSecurityStatus, tooltip=secStatusTooltip)

    @staticmethod
    def ConstructCharacterInfoHomeStation(container):
        CharacterInfoHomeStation(parent=container, name='homeStationCont', align=uiconst.TOTOP, height=CHAR_INFO_ELEMENT_HEIGHT, titleText=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/HomeStationTitle'), valueText='', tooltip='')

    def ConstructCharacterTotalSkillPoints(self, container):
        element = CharacterInfoElement(parent=container, name='birthdateCont', align=uiconst.TOTOP, height=CHAR_INFO_ELEMENT_HEIGHT, titleText=GetByLabel('UI/CharacterSheet/TotalSkillPoints'), valueText='')
        self._UpdateNumberOfSkillPoints(element.valueLabel)
        self.updateSkillPointsThread = AutoTimer(2000, self._UpdateNumberOfSkillPointsThread, element.valueLabel)

    def ConstructCentralCont(self, toggleFunc):
        serviceCont = FlowContainer(parent=self.centralCont, align=uiconst.TOTOP, contentSpacing=(0, 0), padLeft=LEFT_SIDE_PADDING - 5)
        CloneStateIcon(parent=serviceCont, align=uiconst.NOALIGN, width=50, height=50, origin=ORIGIN_CHARACTERSHEET, left=5)
        expertSystems.StateIcon(parent=serviceCont, align=uiconst.NOALIGN, width=50, height=50)
        toggleBtnCont = ContainerAutoSize(name='toggleBtnCont', parent=self.centralCont, align=uiconst.TOPRIGHT, pos=(RIGHT_SIDE_PADDING,
         5,
         0,
         50))
        self.ConstructToggleBtn(toggleBtnCont, toggleFunc)

    def ConstructBottomCont(self, charinfo):
        mainCont = Container(parent=self.bottomCont, name='mainCont', align=uiconst.TOALL)
        bgCont = Container(parent=self.bottomCont, name='bgCont', align=uiconst.TOALL)
        iconsButtonCont = Container(parent=mainCont, align=uiconst.TOBOTTOM, height=71)
        self.charInfoCont = ContainerAutoSize(parent=mainCont, name='charInfoCont', align=uiconst.TOBOTTOM, padLeft=LEFT_SIDE_PADDING, padBottom=12)
        self.ConstructCharacterInfo(charinfo)
        bottomRightCont = Container(parent=iconsButtonCont, name='bottomRightCont', align=uiconst.BOTTOMRIGHT, width=202, height=71)
        Button(parent=bottomRightCont, name='skillsBtn', align=uiconst.CENTERRIGHT, label=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skills'), left=RIGHT_SIDE_PADDING, func=self.OnSkillsBtnClicked)
        bottomLeftCont = ContainerAutoSize(parent=iconsButtonCont, name='bottomLeftCont', align=uiconst.BOTTOMLEFT, pos=(BOTTOM_ICONS_PADDING,
         BOTTOM_ICONS_PADDING,
         0,
         IconButtonCont.default_width))
        self.ConstructCorpIcon(bottomLeftCont)
        if session.allianceid:
            self.ConstructAllianceIcon(bottomLeftCont)
        if session.warfactionid:
            self.ConstructFactionalWarfareIcon(bottomLeftCont)
        Fill(parent=bgCont, name='bg', align=uiconst.TOBOTTOM_NOPUSH, height=BOTTOM_CONT_HEIGHT, color=(0, 0, 0, 0.6))

    def ConstructFactionalWarfareIcon(self, container):
        factionName = cfg.eveowners.Get(session.warfactionid).name
        pirateIds = [500010, 500011]
        if session.warfactionid in pirateIds:
            func = uicore.cmd.OpenInsurgencyDashboard
        else:
            func = uicore.cmd.OpenMilitia
        buttonCont = IconButtonCont(parent=container, func=func, padLeft=2, hint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/FactionalWarfare', factionName=factionName))
        LogoIcon(parent=buttonCont, state=uiconst.UI_DISABLED, align=uiconst.TOALL, itemID=session.warfactionid, ignoreSize=True)

    def ConstructAllianceIcon(self, container):
        buttonCont = IconButtonCont(parent=container, func=self.OnAllianceLogoClick, padLeft=2, hint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Alliance', allianceName=cfg.eveowners.Get(session.allianceid).name))
        allianceIcon = Sprite(parent=buttonCont, state=uiconst.UI_DISABLED, align=uiconst.TOALL, ownerID=session.allianceid)
        sm.GetService('photo').GetAllianceLogo(session.allianceid, 128, allianceIcon, orderIfMissing=True)

    def ConstructCorpIcon(self, container):
        corpName = cfg.eveowners.Get(session.corpid).name
        buttonCont = IconButtonCont(parent=container, func=self.OnCorpIconClick, padLeft=2, hint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Corporation', corpName=corpName))
        GetLogoIcon(parent=buttonCont, state=uiconst.UI_DISABLED, align=uiconst.TOALL, itemID=session.corpid, ignoreSize=True)

    def OnCorpIconClick(self):
        sm.GetService('info').ShowInfo(typeID=const.typeCorporation, itemID=session.corpid)

    def OnAllianceLogoClick(self):
        sm.GetService('info').ShowInfo(const.typeAlliance, itemID=session.allianceid)

    def OnSkillsBtnClicked(self, *args):
        from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
        SkillPlanDockablePanel.Open()

    def ConstructAvatarPreview(self):
        self.avatarHeaderPreview = AvatarHeaderPreview(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        bgCont = Container(name='bgCont', parent=self, state=uiconst.UI_DISABLED)
        Sprite(parent=bgCont, align=uiconst.TOPLEFT, texturePath=self.GetBackground(), width=400, height=1180)

    @staticmethod
    def GetBackground():
        raceID = session.raceID
        if raceID == appConst.raceMinmatar:
            return 'res:/UI/Texture/classes/CharacterSheet/minmatar_bg.png'
        if raceID == appConst.raceAmarr:
            return 'res:/UI/Texture/classes/CharacterSheet/amarr_bg.png'
        if raceID == appConst.raceGallente:
            return 'res:/UI/Texture/classes/CharacterSheet/gallente_bg.png'
        if raceID == appConst.raceCaldari:
            return 'res:/UI/Texture/classes/CharacterSheet/caldari_bg.png'

    def _UpdateNumberOfSkillPointsThread(self, label):
        if self.destroyed:
            self.updateSkillPointsThread = None
            return
        self._UpdateNumberOfSkillPoints(label)

    def _UpdateNumberOfSkillPoints(self, label):
        totalSkillPoints = sm.GetService('skillqueue').GetEstimatedTotalSkillPoints()
        label.text = FmtAmt(totalSkillPoints) if totalSkillPoints else '-'
