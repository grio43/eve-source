#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\steps\sections\chooseNameSection.py
import uthread2
import utillib
from carbonui import const as uiconst
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from carbonui.util.color import Color
from charactercreator import const as ccConst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.common.lib import appConst
from localization import GetByLabel
padding = 16
VALID = 1
invalidNameReasonNamesByID = {-1: 'UI/CharacterCreation/InvalidName/TooShort',
 -2: 'UI/CharacterCreation/InvalidName/TooLong',
 -5: 'UI/CharacterCreation/InvalidName/IllegalCharacter',
 -6: 'UI/CharacterCreation/InvalidName/TooManySpaces',
 -7: 'UI/CharacterCreation/InvalidName/ConsecutiveSpaces',
 -101: 'UI/CharacterCreation/InvalidName/Unavailable',
 -102: 'UI/CharacterCreation/InvalidName/Unavailable'}

class ChooseNameSection(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(ChooseNameSection, self).ApplyAttributes(attributes)
        self.isCheckingName = False
        self.namesChecked = {}
        self.checkNameValidThread = None
        if not uicore.layer.charactercreation.controller.CanChangeName():
            return
        self.contentContainer = ContainerAutoSize(name='contentContainer', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, padding=padding)
        self.contentContainer.isTopLevelWindow = True
        self._ConstructBackground()
        self._ConstructNameSelectionLabel()
        self._ConstructInfoContainer()
        self._ConstructNameEdit()
        self._ConstructBottomCont()
        if self.GetCharacterNameEntered():
            self.CheckAvailability()

    def _ConstructBackground(self):
        Frame(name='hiliteFrame', bgParent=self, frameConst=ccConst.MAINFRAME_INV)
        Fill(name='fill', bgParent=self, color=(0.0, 0.0, 0.0, 0.5))

    def GetInfo(self):
        return uicore.layer.charactercreation.controller.GetInfo()

    def _ConstructInfoContainer(self):
        infoCont = Container(name='infoContainer', parent=self.contentContainer, align=uiconst.TOTOP, height=16, top=2)
        EveLabelMedium(name='fullNameLabel', parent=infoCont, align=uiconst.TOLEFT, opacity=0.75, text=GetByLabel('UI/CharacterCreation/FullName'))
        MoreInfoIcon(name='moreInfoIcon', parent=infoCont, align=uiconst.TOLEFT, hint=GetByLabel('UI/CharacterCreation/NameConstraintsHint'), left=5)

    def _ConstructNameSelectionLabel(self):
        text = CCLabel(name='nameSelectionLabel', parent=self.contentContainer, text=GetByLabel('UI/CharacterCreation/NameSelection'), fontsize=20, align=uiconst.TOTOP, letterspace=1, top=-6, uppercase=1, color=eveColor.PRIMARY_BLUE, state=uiconst.UI_DISABLED)

    def _ConstructNameEdit(self):
        editContainer = Container(name='editContainer', parent=self.contentContainer, align=uiconst.TOTOP, height=30, top=3)
        self.checkAvailabilityIcon = Icon(name='checkAvailabilityIcon', parent=Container(parent=editContainer, align=uiconst.TORIGHT, width=16, padLeft=8), align=uiconst.CENTER, pos=(0, 0, 20, 20), state=uiconst.UI_HIDDEN)
        self.nameEdit = SingleLineEditText(name='nameEdit', setvalue=self.GetInfo().charName or '', parent=editContainer, maxLength=appConst.maximumCharacterNameLength, align=uiconst.TOALL, OnChange=self.OnTextEditChange, OnSetFocus=self.OnFirstNameFocus, color=(1.0, 1.0, 1.0, 1.0), hintText=GetByLabel('UI/CharacterCreation/FirstName'), fontsize=16, width=5, height=0)
        self.nameEdit.OnReturn = self.CheckAvailability
        self.nameEdit.OnAnyChar = self.OnCharInName

    def _ConstructBottomCont(self):
        bottomCont = Container(name='bottomCont', parent=self.contentContainer, align=uiconst.TOTOP, height=16, state=uiconst.UI_PICKCHILDREN, top=5, padRight=20)
        self.checkAvailabilityLabel = EveLabelMedium(name='checkAvailabilityLabel', parent=bottomCont, align=uiconst.TOLEFT, width=300, state=uiconst.UI_DISABLED, color=Color.RED, opacity=0.75)
        self.charCounterLabel = EveLabelMedium(name='charCounterLabel', parent=bottomCont, align=uiconst.CENTERRIGHT, opacity=0.75, text=self.CountRemainingCharacters())
        buttonCont = ContainerAutoSize(parent=self.contentContainer, align=uiconst.TOTOP, padTop=4)
        Button(name='randomizeLastNameButton', parent=buttonCont, label=GetByLabel('UI/CharacterCreation/Randomize'), align=uiconst.TOPLEFT, func=self.RandomizeName)

    def RandomizeName(self, *args):
        name = sm.RemoteSvc('charUnboundMgr').GetValidRandomName(self.GetInfo().raceID)
        self.CacheNameValid(name, True)
        self.nameEdit.SetValue(name, docallback=False)
        self.UpdateIsValidIconAndText(VALID)
        uicore.layer.charactercreation.controller.metrics.last_name_randomized()
        uicore.layer.charactercreation.controller.SetNameCallback(name)
        self.charCounterLabel.SetText(self.CountRemainingCharacters())

    def OnTextEditChange(self, *args):
        self.checkAvailabilityLabel.state = uiconst.UI_HIDDEN
        self.checkAvailabilityIcon.state = uiconst.UI_HIDDEN
        if self.checkNameValidThread:
            self.checkNameValidThread.kill()
        self.checkNameValidThread = uthread2.start_tasklet(self._CheckNameValidThread)
        self.charCounterLabel.SetText(self.CountRemainingCharacters())

    def CountRemainingCharacters(self):
        nameLength = len(self.nameEdit.GetText())
        remainingAllowedCharacters = appConst.maximumCharacterNameLength - nameLength
        if remainingAllowedCharacters < 0:
            return 0
        return remainingAllowedCharacters

    def _CheckNameValidThread(self):
        uthread2.Sleep(1.0)
        self.CheckAvailability()

    def OnFirstNameFocus(self, *args):
        uicore.layer.charactercreation.controller.metrics.first_name_focused()

    def OnLastNameFocus(self, *args):
        uicore.layer.charactercreation.controller.metrics.last_name_focused()

    def OnCharInName(self, char, *args):
        if char == uiconst.VK_SPACE:
            allowedNumSpaces = 2
            numSpaces = self.nameEdit.text.count(' ')
            if numSpaces >= allowedNumSpaces:
                return False
        return True

    def OnCharInLastName(self, char, *args):
        if char == uiconst.VK_SPACE:
            return False
        return True

    def CheckAvailability(self, *args):
        if self.isCheckingName:
            return
        self.isCheckingName = True
        try:
            charName = self.GetCharacterNameEntered()
            self.NotifyCCLayerOfAvailabilityCheck(charName)
            isValidCode = self.IsNameValid(charName)
            self.UpdateIsValidIconAndText(isValidCode)
            isAvailable = utillib.KeyVal()
            uicore.layer.charactercreation.controller.metrics.name_available_checked(isValidCode)
            if isValidCode == VALID:
                isAvailable.charName = charName
                isAvailable.reason = ''
                return isAvailable
            isAvailable.charName = None
            isAvailable.reason = self.GetIsValidText(isValidCode)
            return isAvailable
        finally:
            self.isCheckingName = False
            self.checkNameValidThread = None

    def GetIsValidText(self, isValidCode):
        if isValidCode == VALID:
            return ''
        reason = invalidNameReasonNamesByID.get(isValidCode, 'UI/CharacterCreation/InvalidName/IllegalCharacter')
        return GetByLabel(reason)

    def UpdateIsValidIconAndText(self, isValidCode):
        self.checkAvailabilityIcon.state = uiconst.UI_DISABLED
        self.checkAvailabilityLabel.state = uiconst.UI_DISABLED
        if isValidCode == VALID:
            texturePath = 'res:/UI/Texture/Icons/38_16_193.png'
            self.checkAvailabilityIcon.SetRGBA(*Icon.default_color)
        else:
            texturePath = 'res:/UI/Texture/classes/Moonmining/warning.png'
            self.checkAvailabilityIcon.SetRGBA(*Color.RED)
        self.checkAvailabilityIcon.SetTexturePath(texturePath)
        self.checkAvailabilityLabel.text = self.GetIsValidText(isValidCode)

    def GetCharacterNameEntered(self):
        charName = self.nameEdit.GetValue().strip()
        self.nameEdit.CloseHistoryMenu()
        uicore.layer.charactercreation.controller.SetNameCallback(charName)
        return charName

    def IsNameValid(self, charName):
        if charName in self.namesChecked:
            isValid = self.namesChecked[charName]
        else:
            isValid = sm.RemoteSvc('charUnboundMgr').ValidateNameEx(charName, len(self.namesChecked))
            self.CacheNameValid(charName, isValid)
        return isValid

    def CacheNameValid(self, charName, isValid):
        self.namesChecked[charName] = isValid

    def NotifyCCLayerOfAvailabilityCheck(self, name):
        uicore.layer.charactercreation.controller.OnAvailabilityCheck(name)
