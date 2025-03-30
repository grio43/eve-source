#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\steps\characterNaming.py
import blue
from carbonui import const as uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.uianimations import animations
from charactercreator import const as ccConst
from characterdata.schools import get_school_ids_by_race_id
from characterdata.schools import get_school
from characterdata.schools import get_school_description
from characterdata.schools import get_school_name
from characterdata.schools import get_school_title
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.login.charcreation import ccUtil
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation.hexes import CCHexButtonSchool
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.steps.sections.chooseNameSection import ChooseNameSection
from eve.common.lib import appConst as const
import localization
import random
from localization.util import AmOnChineseServer
padding = 16
topRightPushContainerMaxHeight = 130
topRightPushContainerMinHeight = 16

class CharacterNaming(BaseCharacterCreationStep):
    __notifyevents__ = ['OnHideUI', 'OnShowUI']
    stepID = ccConst.NAMINGSTEP

    def ApplyAttributes(self, attributes):
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        self.schoolInfo = {}
        self.schoolConts = {}
        self.educationCont = None
        self.startEducationHeight = 180
        self.topRightPushContainer = Container(name='topRightPushContainer', parent=self.rightSide, height=topRightPushContainerMaxHeight, align=uiconst.TOTOP)
        self.rightSideContentContainer = ContainerAutoSize(name='rightSideContentContainer', parent=self.rightSide, align=uiconst.TOTOP)
        self.rightSideAlignContainer = ContainerAutoSize(name='rightSideAlignContainer', parent=self.rightSideContentContainer, align=uiconst.TOPRIGHT, width=410, top=0, left=10)
        self.SetupEducationSection()
        self.SetupNameSection()
        contentContainer = ContainerAutoSize(name='contentContainer', parent=self.leftSide, align=uiconst.TOPLEFT, top=130, width=128, left=25)
        self.portraitCont = Container(name='portraitCont', parent=contentContainer, align=uiconst.TOTOP, height=128)
        Frame(parent=self.portraitCont, color=ccConst.COLOR + (0.3,))
        self.facePortrait = Icon(parent=self.portraitCont, idx=1, align=uiconst.CENTER, pos=(0, 0, 128, 128))
        self.UpdatePortraitPhoto()
        self.UpdateLayout()

    def UpdatePortraitPhoto(self):
        photo = uicore.layer.charactercreation.controller.GetActivePortrait()
        if photo is not None:
            self.facePortrait.texture.atlasTexture = photo
            self.facePortrait.texture.atlasTexture.Reload()

    def SetupNameSection(self):
        contHeight = 120 if AmOnChineseServer() else 160
        self.nameCont = ChooseNameSection(name='nameSelectionContainer', parent=self.rightSideAlignContainer, align=uiconst.TOTOP, height=contHeight, padding=(0,
         padding,
         0,
         0), state=uiconst.UI_PICKCHILDREN)

    def UpdateLayout(self):
        info = self.GetInfo()
        self.AdjustHeightAndWidth(doMorph=0)
        try:
            self.SetSchoolFromID(info.schoolID, doMorph=0)
        except Exception:
            if self and not self.destroyed:
                raise

    def SetupEducationSection(self, *args):
        info = self.GetInfo()
        if self.educationCont:
            self.educationCont.Close()
        self.educationCont = Container(name='educationCont', parent=self.rightSideAlignContainer, align=uiconst.TOTOP, height=self.startEducationHeight, padding=(0,
         padding,
         padding,
         0))
        sub = Container(name='sub', parent=self.educationCont, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=(padding,
         padding,
         padding,
         padding))
        topCont = Container(name='topCont', parent=sub, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, pos=(0, 20, 0, 64))
        text = CCLabel(state=uiconst.UI_NORMAL, parent=sub, text=localization.GetByLabel('UI/CharacterCreation/EducationSelection'), fontsize=20, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, -6, 0, 0), uppercase=1, color=eveColor.PRIMARY_BLUE)
        text.hint = localization.GetByLabel('UI/CharacterCreation/HelpTexts/chooseEducationHint')
        self.schoolTextCont = textCont = Container(name='textCont', parent=sub, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.schoolNameText = CCLabel(parent=textCont, text='', fontsize=14, align=uiconst.TOPLEFT, letterspace=1, idx=1, pos=(0, 0, 0, 0), color=ccConst.COLOR50)
        self.schoolTitleText = CCLabel(parent=textCont, text='', fontsize=12, align=uiconst.TOPLEFT, letterspace=1, idx=1, padTop=20, color=ccConst.COLOR50)
        self.schoolDescrText = CCLabel(parent=textCont, text='', fontsize=fontconst.EVE_SMALL_FONTSIZE, align=uiconst.TOTOP, letterspace=0, idx=1, padTop=40, shadowOffset=(0, 0), bold=0, color=ccConst.COLOR50)
        Frame(name='hiliteFrame', parent=self.educationCont, frameConst=ccConst.MAINFRAME_INV)
        Fill(name='fill', parent=self.educationCont, color=(0.0, 0.0, 0.0, 0.5))
        if not self.schoolInfo:
            schoolIds = get_school_ids_by_race_id(info.raceID)
            for id in schoolIds:
                info = get_school(id)
                self.schoolInfo[id] = info

        left = 0
        offsetByRace = {const.raceCaldari: 17,
         const.raceMinmatar: 14,
         const.raceAmarr: 11,
         const.raceGallente: 20}
        iconNumOffset = offsetByRace.get(info.raceID)
        for schoolID, info in self.schoolInfo.iteritems():
            c = Container(name='c', parent=topCont, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, pos=(left,
             0,
             115,
             64))
            hexName = get_school_name(schoolID)
            isSchoolDisabled = ccUtil.IsSchoolDisabled(schoolID)
            hex = CCHexButtonSchool(name='schoolHex', parent=c, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, pos=(0, 0, 64, 64), pickRadius=32, info=info, id=schoolID, hexName=hexName, func=self.SetSchool, iconNum=schoolID - iconNumOffset)
            if isSchoolDisabled:
                hex.SetHint(localization.GetByLabel('UI/CharacterCreation/DisabledSchool'))
                hex.clickable = False
            left += 125
            self.schoolConts[schoolID] = hex

    def SetSchoolFromID(self, schoolID, doMorph = 1, *args):
        selected = self.schoolConts.get(schoolID, None)
        self.SetSchool(selected, doMorph=doMorph)

    def SetSchool(self, selected = None, doMorph = 1, *args):
        if selected is None:
            allowedSchools = [ hex for schoolID, hex in self.schoolConts.iteritems() if not ccUtil.IsSchoolDisabled(schoolID) ]
            selected = random.choice(allowedSchools)
        uicore.layer.charactercreation.controller.SelectSchool(selected.id)
        selected.SelectHex(self.schoolConts.values())
        self.schoolNameText.text = get_school_title(selected.id)
        self.schoolTitleText.text = selected.hexName
        self.schoolDescrText.text = get_school_description(selected.id)
        selected.frame.state = uiconst.UI_DISABLED
        self.AdjustHeightAndWidth(doMorph=doMorph)
        uicore.layer.charactercreation.controller.metrics.pick_school(selected.id)

    def CheckAvailability(self, *args):
        return self.nameCont.CheckAvailability()

    def AdjustHeightAndWidth(self, doMorph = 1, *args):
        schoolTextContHeight = self.educationCont.height - 105
        textHeight = self.schoolDescrText.textheight + self.schoolDescrText.padTop
        missingSchoolHeight = textHeight - schoolTextContHeight
        totalMissing = max(missingSchoolHeight, 0)
        if totalMissing > 0:
            for missingHeight, cont in [(missingSchoolHeight, self.educationCont)]:
                if missingHeight < -10:
                    cont.height -= 5
                    blue.synchro.Yield()
                    if self and not self.destroyed:
                        self.AdjustHeightAndWidth(doMorph=doMorph)
                    return

            availableHeight = uicore.desktop.height - self.educationCont.height - self.nameCont.height - 4 * padding
            if availableHeight >= totalMissing:
                if missingSchoolHeight > 0:
                    self.educationCont.height += missingSchoolHeight + 2
            elif self.rightSide.width < uicore.desktop.width * 0.6:
                if doMorph:
                    animations.MorphScalar(self.rightSide, 'width', endVal=self.rightSide.width + 50, duration=0.025, sleep=True)
                else:
                    self.rightSide.width += 50
                    blue.synchro.Yield()
                self.AdjustHeightAndWidth(doMorph=doMorph)
        excessHeight = ccConst.BUTTON_AREA_HEIGHT + self.educationCont.height + self.nameCont.height + 4 * padding + topRightPushContainerMaxHeight - uicore.desktop.height
        if excessHeight > 0:
            adjust = min(excessHeight, topRightPushContainerMaxHeight)
            self.topRightPushContainer.height = max(topRightPushContainerMinHeight, topRightPushContainerMaxHeight - adjust)
        else:
            self.topRightPushContainer.height = topRightPushContainerMaxHeight
