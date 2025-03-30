#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\bloodlineInfo.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from characterdata.bloodlines import get_bloodline_name
from charactercreator.client.empireSelectionData import GetBloodlinesInfo
import charactercreator.client.scalingUtils as ccScalingUtils
from eve.common.lib.appConst import bloodlineAmarr, bloodlineNiKunni, bloodlineKhanid
from eve.common.lib.appConst import bloodlineAchura, bloodlineCivire, bloodlineDeteis
from eve.common.lib.appConst import bloodlineGallente, bloodlineIntaki, bloodlineJinMei
from eve.common.lib.appConst import bloodlineBrutor, bloodlineSebiestor, bloodlineVherokior
from carbonui.fontconst import STYLE_HEADER
from eve.client.script.ui.login.charcreation.charCreationButtons import StaticBloodlineButton
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.util.uix import GetTextWidth
from localization import GetByMessageID
BLOODLINES_INFO_TEXT_HEIGHT = 85
GENDER_BUTTON_MARGIN = 4
BLOODLINES_INFO_HEIGHT = BLOODLINES_INFO_TEXT_HEIGHT + GENDER_BUTTON_MARGIN
BLOODLINES_INFO_ICON_SIZE = 45
BLOODLINES_INFO_ICON_TOP = 25
BLOODLINES_INFO_ICON_TO_NAME_MARGIN = 11
BLOODLINE_NAME_FONTSIZE = 11
BLOODLINES_INFO_TEXT_WIDTH = 498
BLOODLINES_INFO_ICON_TO_TEXT_MARGIN = 10
BLOODLINES_INFO_TITLE_TO_TEXT_MARGIN = 11
BLOODLINES_INFO_WIDTH = BLOODLINES_INFO_ICON_SIZE + BLOODLINES_INFO_ICON_TO_TEXT_MARGIN + BLOODLINES_INFO_TEXT_WIDTH
BLOODLINES_INFO_TITLE_FONTSIZE = 13
BLOODLINES_INFO_TEXT_FONTSIZE = 11
BLOODLINES_INFO_TITLE_OPACITY = 1.0
BLOODLINES_INFO_TEXT_OPACITY = 0.75
BLOODLINE_ICONS_BY_ID = {bloodlineAmarr: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Amarr.png',
 bloodlineKhanid: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Khanid.png',
 bloodlineNiKunni: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Nikunni.png',
 bloodlineGallente: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Gallente.png',
 bloodlineIntaki: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Intaki.png',
 bloodlineJinMei: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Jinmei.png',
 bloodlineDeteis: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Deteis.png',
 bloodlineAchura: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Achura.png',
 bloodlineCivire: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Civire.png',
 bloodlineSebiestor: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Sebiestor.png',
 bloodlineVherokior: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Vherokior.png',
 bloodlineBrutor: 'res:/UI/Texture/classes/EmpireSelection/BloodlineIcons/bloodline_Brutor.png'}

def GetBloodlineInfoContainerWidth():
    return BLOODLINES_INFO_WIDTH * ccScalingUtils.GetScaleFactor()


def GetBloodlineInfoContainerHeight():
    return BLOODLINES_INFO_HEIGHT * ccScalingUtils.GetScaleFactor()


class BloodlineInfoContainer(Container):

    def ApplyAttributes(self, attributes):
        super(BloodlineInfoContainer, self).ApplyAttributes(attributes)
        self.raceID = attributes.raceID
        self.bloodlineIDs = attributes.bloodlineIDs
        self.selectedBloodlineID = attributes.selectedBloodlineID
        self.bloodlineButtonsByBloodline = {}
        self.bloodlineTitlesByBloodline = {}
        self.containersByBloodline = {}
        self.bloodlineBtns = []
        self.hoveredBloodlineID = None
        self.displayedBloodlineID = None
        bloodlineInfoContainerWidth = GetBloodlineInfoContainerWidth()
        bloodlineInfoContainerHeight = GetBloodlineInfoContainerHeight()
        self.contentContainer = Container(name='contentContainer', parent=self, align=uiconst.CENTER, width=bloodlineInfoContainerWidth, height=bloodlineInfoContainerHeight)
        self.ConstructLogos()
        self.ConstructText()
        self.SwitchBloodlines()

    def ConstructLogos(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        logoSize = BLOODLINES_INFO_ICON_SIZE * scaleFactor
        marginToName = BLOODLINES_INFO_ICON_TO_NAME_MARGIN * scaleFactor
        nameHeight = BLOODLINE_NAME_FONTSIZE * scaleFactor
        iconContainerWidth = logoSize
        iconContainerHeight = logoSize + marginToName + nameHeight
        iconContainerTop = BLOODLINES_INFO_ICON_TOP * scaleFactor
        bloodlineNameFontsize = BLOODLINE_NAME_FONTSIZE * scaleFactor
        for bloodlineID in self.bloodlineIDs:
            cont = self.containersByBloodline[bloodlineID] = Container(name='cont_%i' % bloodlineID, parent=self.contentContainer, align=uiconst.TOPLEFT, width=iconContainerWidth, height=iconContainerHeight, opacity=0.0, top=iconContainerTop)
            btn = StaticBloodlineButton(name='bloodlineBtn_%d' % bloodlineID, parent=cont, align=uiconst.TOTOP, pos=(0,
             0,
             logoSize,
             logoSize), iconTexturePath=BLOODLINE_ICONS_BY_ID[bloodlineID])
            bloodlineName = get_bloodline_name(bloodlineID)
            bloodlineNameWidth = GetTextWidth(strng=bloodlineName, fontsize=bloodlineNameFontsize, hspace=0, uppercase=True)
            bloodlineTitle = CCLabel(name='bloodlineName_%s' % bloodlineName, parent=cont, fontsize=bloodlineNameFontsize, align=uiconst.BOTTOMLEFT, text=bloodlineName.upper(), letterspace=0, top=0, bold=0, left=iconContainerWidth / 2 - bloodlineNameWidth / 2)
            self.bloodlineTitlesByBloodline[bloodlineID] = bloodlineTitle
            self.bloodlineButtonsByBloodline[bloodlineID] = btn
            self.bloodlineBtns.append(btn)

    def ConstructText(self):
        bloodlineInfoContainerHeight = GetBloodlineInfoContainerHeight()
        scaleFactor = ccScalingUtils.GetScaleFactor()
        textWidth = BLOODLINES_INFO_TEXT_WIDTH * scaleFactor
        self.textCont = Container(name='bloodlineTextCont', parent=self.contentContainer, align=uiconst.TORIGHT, width=textWidth, height=bloodlineInfoContainerHeight, state=uiconst.UI_NORMAL)
        self.textContCentered = Container(name='bloodlineTextContCentered', parent=self.textCont, align=uiconst.CENTER, width=textWidth, height=bloodlineInfoContainerHeight, state=uiconst.UI_NORMAL)
        self.title = CCLabel(parent=self.textContCentered, fontsize=BLOODLINES_INFO_TITLE_FONTSIZE * scaleFactor, align=uiconst.TOTOP, text='', letterspace=0, top=0, bold=0, fontStyle=STYLE_HEADER, opacity=BLOODLINES_INFO_TITLE_OPACITY)
        self.text = CCLabel(parent=self.textContCentered, fontsize=BLOODLINES_INFO_TEXT_FONTSIZE * scaleFactor, align=uiconst.TOTOP, text='', letterspace=0, top=0, bold=0, fontStyle=STYLE_HEADER, opacity=BLOODLINES_INFO_TEXT_OPACITY, padTop=BLOODLINES_INFO_TITLE_TO_TEXT_MARGIN * scaleFactor)

    def GetInfo(self):
        return self.parent.GetInfo()

    def AlignButtonIcons(self, bloodlineID, left):
        if self.displayedBloodlineID is not None:
            return
        scaleFactor = ccScalingUtils.GetScaleFactor()
        logoSize = BLOODLINES_INFO_ICON_SIZE * scaleFactor
        marginToName = BLOODLINES_INFO_ICON_TO_NAME_MARGIN * scaleFactor
        nameHeight = BLOODLINE_NAME_FONTSIZE * scaleFactor
        nameFontsize = BLOODLINE_NAME_FONTSIZE * scaleFactor
        containerSizeDifference = ccScalingUtils.GetMainPanelWidth() - GetBloodlineInfoContainerWidth()
        containerWidth = logoSize
        containerHeight = logoSize + marginToName + nameHeight
        cont = self.containersByBloodline[bloodlineID]
        cont.left = left - containerWidth / 2 - containerSizeDifference / 2
        cont.state = uiconst.UI_PICKCHILDREN
        cont.width = containerWidth
        cont.height = containerHeight
        label = self.bloodlineTitlesByBloodline[bloodlineID]
        bloodlineName = get_bloodline_name(bloodlineID)
        nameWidth = GetTextWidth(strng=bloodlineName, fontsize=nameFontsize, hspace=0, uppercase=True)
        label.left = containerWidth / 2 - nameWidth / 2

    def ShowLogos(self):
        for logo in self.containersByBloodline.values():
            logo.opacity = 1.0

    def ShowBloodlineNames(self):
        for label in self.bloodlineTitlesByBloodline.values():
            label.opacity = 1.0

    def HideBloodlineNames(self):
        for label in self.bloodlineTitlesByBloodline.values():
            label.opacity = 0.0

    def ShowText(self):
        self.textCont.display = True

    def HideText(self):
        self.textCont.display = False

    def SelectBloodline(self, bloodlineID):
        self.selectedBloodlineID = bloodlineID

    def StopLogoAnimations(self):
        for bloodlineID in self.bloodlineIDs:
            logo = self.containersByBloodline[bloodlineID]
            uicore.animations.StopAllAnimations(logo)

    def SwitchBloodlines(self):
        self.StopLogoAnimations()
        if self.hoveredBloodlineID is not None:
            self.displayedBloodlineID = self.hoveredBloodlineID
        elif self.selectedBloodlineID is not None:
            self.displayedBloodlineID = self.selectedBloodlineID
        if self.displayedBloodlineID is None:
            self.ShowBloodlineNames()
            self.ShowLogos()
            self.HideText()
            return
        self.ShowText()
        self.HideBloodlineNames()
        for bloodlineID in self.bloodlineIDs:
            logo = self.containersByBloodline[bloodlineID]
            logo.left = 0
            logo.top = 0
            if bloodlineID != self.displayedBloodlineID:
                logo.opacity = 0.0
            else:
                logo.opacity = 1.0
                bloodlineTitle = get_bloodline_name(bloodlineID)
                bloodlineDescriptionLabel = GetBloodlinesInfo(self.raceID)[bloodlineID]
                bloodlineDescription = GetByMessageID(bloodlineDescriptionLabel)
                self.title.text = bloodlineTitle.upper()
                self.text.text = bloodlineDescription

    def HoverBloodline(self, bloodlineID):
        if bloodlineID != self.hoveredBloodlineID:
            self.hoveredBloodlineID = bloodlineID
            self.SwitchBloodlines()

    def ResetInfo(self):
        self.hoveredBloodlineID = None
        self.displayedBloodlineID = None
        if not self.selectedBloodlineID:
            for bloodlineID in self.bloodlineIDs:
                logo = self.containersByBloodline[bloodlineID]
                scaleFactor = ccScalingUtils.GetScaleFactor()
                iconContainerTop = BLOODLINES_INFO_ICON_TOP * scaleFactor
                logo.top = iconContainerTop

        self.SwitchBloodlines()

    def UpdateLayout(self):
        scaleFactor = ccScalingUtils.GetScaleFactor()
        bloodlineInfoContainerWidth = GetBloodlineInfoContainerWidth()
        bloodlineInfoContainerHeight = GetBloodlineInfoContainerHeight()
        textWidth = BLOODLINES_INFO_TEXT_WIDTH * scaleFactor
        self.contentContainer.width = bloodlineInfoContainerWidth
        self.contentContainer.height = bloodlineInfoContainerHeight
        self.textCont.width = textWidth
        self.textCont.height = bloodlineInfoContainerHeight
        self.textContCentered.width = textWidth
        self.textContCentered.height = bloodlineInfoContainerHeight
        self.title.fontsize = BLOODLINES_INFO_TITLE_FONTSIZE * scaleFactor
        self.text.fontsize = BLOODLINES_INFO_TEXT_FONTSIZE * scaleFactor
        self.text.padTop = BLOODLINES_INFO_TITLE_TO_TEXT_MARGIN * scaleFactor
        logoSize = BLOODLINES_INFO_ICON_SIZE * scaleFactor
        marginToName = BLOODLINES_INFO_ICON_TO_NAME_MARGIN * scaleFactor
        nameHeight = BLOODLINE_NAME_FONTSIZE * scaleFactor
        nameFontsize = BLOODLINE_NAME_FONTSIZE * scaleFactor
        iconContainerWidth = logoSize
        iconContainerHeight = logoSize + marginToName + nameHeight
        iconContainerTop = BLOODLINES_INFO_ICON_TOP * scaleFactor
        for cont in self.containersByBloodline.values():
            cont.width = iconContainerWidth
            cont.height = iconContainerHeight
            cont.top = iconContainerTop

        for btn in self.bloodlineBtns:
            btn.Resize(logoSize, logoSize)

        for bloodlineID, label in self.bloodlineTitlesByBloodline.iteritems():
            nameWidth = GetTextWidth(strng=get_bloodline_name(bloodlineID), fontsize=nameFontsize, hspace=0, uppercase=True)
            label.fontsize = nameFontsize
            label.left = iconContainerWidth / 2 - nameWidth / 2

        self.SwitchBloodlines()
