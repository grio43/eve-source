#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\zhReport\reportWindow.py
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionSmall
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from localization import GetByLabel
TYPE_INAPPROPRIATE_LANGUAGE = 1
TYPE_OFFENSIVE_MAIL = 2
TYPE_MACRO_USE = 3
TYPE_QUESTIONABLE_TRANSACTION = 4
TYPE_INAPPROPRIATE_CHARACTER_NAME = 5
TYPE_EXPLOIT_ABUSE = 6
TYPE_GAMBLING = 7
TYPE_OTHER = 8
INVALID_CHARACTER_ID = -1
INAPPROPRIATE_COMBO_OPTIONS = ((GetByLabel('UI/Kiring/Report/OffensiveMail'), TYPE_OFFENSIVE_MAIL, GetByLabel('UI/Kiring/Report/OffensiveMailHint')),
 (GetByLabel('UI/Kiring/Report/InappropriateLanguage'), TYPE_INAPPROPRIATE_LANGUAGE, GetByLabel('UI/Kiring/Report/InappropriateLanguageHint')),
 (GetByLabel('UI/Kiring/Report/MacroUse'), TYPE_MACRO_USE, GetByLabel('UI/Kiring/Report/MacroUseHint')),
 (GetByLabel('UI/Kiring/Report/QuestionableTransaction'), TYPE_QUESTIONABLE_TRANSACTION, GetByLabel('UI/Kiring/Report/QuestionableTransactionHint')),
 (GetByLabel('UI/Kiring/Report/InappropriateCharacterName'), TYPE_INAPPROPRIATE_CHARACTER_NAME, GetByLabel('UI/Kiring/Report/InappropriateCharacterNameHint')),
 (GetByLabel('UI/Kiring/Report/ExploitAbuse'), TYPE_EXPLOIT_ABUSE, GetByLabel('UI/Kiring/Report/ExploitAbuseHint')),
 (GetByLabel('UI/Kiring/Report/Gambling'), TYPE_GAMBLING, GetByLabel('UI/Kiring/Report/GamblingHint')),
 (GetByLabel('UI/Kiring/Report/Other'), TYPE_OTHER, GetByLabel('UI/Kiring/Report/OtherHint')))

class ReportWindow(Window):
    __guid__ = 'form.ReportWindow'
    default_windowID = 'form.reportWnd'
    default_captionLabelPath = 'UI/Kiring/Report/WndReportCaption'
    default_descriptionLabelPath = 'UI/Kiring/Report/WndReportDescription'
    default_iconNum = 'res:/ui/Texture/WindowIcons/log.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.reportedCharID = INVALID_CHARACTER_ID
        self.SetMinSize([340, 460])
        self.MakeUnResizeable()
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=60, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.label = eveLabel.WndCaptionLabel(parent=self.topParent, text=GetByLabel(self.default_captionLabelPath))
        self._ConstructLayout()

    def _ConstructLayout(self):
        bottomCont = Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=20, padding=(0, 0, 0, 4))
        infoCont = Container(name='reportedInfoCont', parent=self.sr.main, align=uiconst.TOTOP, height=160, padding=(4, -8, 4, 4))
        Fill(name='backGround', parent=infoCont, color=(0.5, 0.5, 0.5, 0.1), align=uiconst.TOALL, padding=(4, 11, 4, 10))
        self.reportedImgCont = Container(name='imgCont', parent=infoCont, align=uiconst.TOLEFT, width=128, padding=(10, 17, 0, 0), pos=(0, 0, 64, 0))
        reportedNameCont = Container(name='nameCont', parent=infoCont, align=uiconst.TOLEFT, width=200, padding=(75, 0, 0, 0))
        self.reportedCharacter = EveCaptionSmall(parent=reportedNameCont, left=0, top=0, align=uiconst.CENTERLEFT, width=180, state=uiconst.UI_DISABLED, idx=0)
        midCont = Container(name='inappropriateInfoCont', parent=self.sr.main, align=uiconst.TOALL)
        EveLabelMedium(text=GetByLabel('UI/Kiring/Report/InappropriateType'), parent=midCont, align=uiconst.TOPLEFT, padLeft=8)
        self.inappropriateType = Combo(name='inappropriateType', parent=midCont, options=self._GetComboOptions(), select=TYPE_OFFENSIVE_MAIL, width=200, pos=(131, 0, 0, 0), callback=self._OnComboOptionChange)
        self.inappropriateType.Confirm()
        additionalCont = Container(parent=midCont, align=uiconst.TOALL, padTop=25)
        EveLabelMedium(text=GetByLabel('UI/Kiring/Report/AdditionalInformation'), parent=additionalCont, align=uiconst.TOPLEFT, padLeft=8)
        self.additionalInfo = EditPlainText(name='information', parent=additionalCont, align=uiconst.TOALL, padding=(8, 24, 8, 4))
        Button(name='submit', parent=bottomCont, align=uiconst.CENTER, label=GetByLabel('UI/Kiring/Report/ButtonSubmit'), fixedwidth=64, func=self._Submit)

    def _GetComboOptions(self):
        return INAPPROPRIATE_COMBO_OPTIONS

    def _OnComboOptionChange(self, combo, key, value):
        if value == TYPE_INAPPROPRIATE_LANGUAGE:
            focus_window = sm.GetService('focus').GetFocusChannel()
            channelName = sm.GetService('XmppChat').GetDetailedDisplayName(focus_window.GetChannelId())
            messageCount = 0
            messageText = '%s\n' % channelName
            for sender, text, timestamp, colorkey in focus_window.messages:
                if sender == self.reportedCharID:
                    messageCount += 1
                    messageText += '[%s] %s> %s\n' % (FmtDate(timestamp), cfg.eveowners.Get(sender).name, text)

            if messageCount > 0:
                self.additionalInfo.SetValue(messageText)
            else:
                self.additionalInfo.SetValue('')
        else:
            self.additionalInfo.SetValue('')

    def _Submit(self, *args):
        if self.reportedCharID != INVALID_CHARACTER_ID:
            sm.GetService('reportClientSvc').SubmitReportInformation(self.reportedCharID, self.inappropriateType.GetValue(), self.additionalInfo.GetValue())
            self.CloseByUser()
            eve.Message('CustomInfo', {'info': GetByLabel('UI/Messages/ReportSuccessfullyBody')})

    def SetReportedCharacter(self, characterId):
        characterName = cfg.eveowners.Get(characterId).name
        if characterName:
            self.reportedCharID = characterId
            self.reportedCharacter.SetText(characterName)
            eveIcon.GetOwnerLogo(self.reportedImgCont, self.reportedCharID, size=128, noServerCall=True)
        else:
            raise RuntimeError('Invalid character id: %d' % characterId)
