#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\help.py
import blue
import carbonui.const as uiconst
import localization
import utillib
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import CaptionLabel, EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import LineThemeColored, SpriteThemeColored
from eveservices.xmppchat import GetChatService
from globalConfig.getFunctions import ShouldShowBugreportButton
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
HELP_WINDOW_WIDTH = 300
ENTRY_WIDTH = 287
MIN_ENTRY_HEIGHT = 36
ENTRY_TEXT_WIDTH = 222
ENTRY_PADDING_TOP = 4

class HelpWindow(Window):
    __notifyevents__ = ['ProcessSessionChange']
    default_width = HELP_WINDOW_WIDTH
    default_fixedWidth = 400
    default_height = 400
    default_windowID = 'help'
    default_captionLabelPath = 'UI/Help/EveHelp'
    default_descriptionLabelPath = 'Tooltips/Neocom/Help_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/help.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MouseDown = self.OnWndMouseDown
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, callback=self._OnMainContAutoSized)
        self.ConstructContent()

    def ConstructTopParent(self):
        self.topParent = Container(name='topParent', parent=self.mainCont, align=uiconst.TOTOP, height=64, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        CaptionLabel(text=localization.GetByLabel('UI/Help/EveHelp'), parent=self.topParent, align=uiconst.CENTERLEFT, left=70)

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Close()

    def CreateBugReport(self, *args):
        buttons = [utillib.KeyVal(label=localization.GetByLabel('UI/Help/ReportBug'), id='BugReport')]
        petitionerSvc = sm.RemoteSvc('petitioner')
        if petitionerSvc.IsZendeskSwapEnabled():
            buttons.append(utillib.KeyVal(label=localization.GetByLabel('UI/Help/HelpCenter'), id='Help'))
        else:
            buttons.append(utillib.KeyVal(label=localization.GetByLabel('UI/Common/Cancel'), id=uiconst.ID_CANCEL))
        ret = uicore.Message('BugReportOpenConfirmation', {}, buttons, default='BugReport')
        if ret == 'BugReport':
            self.Close()
            blue.pyos.synchro.SleepWallclock(10)
            sm.GetService('bugReporting').StartCreateBugReport()
        elif ret == 'Help':
            self.OpenHelpCenter()

    def _LoadSupportHelpChannel(self, parent):
        EveLabelMedium(name='joinChannelHint', text=localization.GetByLabel('UI/Help/JoinChannelHint'), parent=parent, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
        helpbtnparent = ContainerAutoSize(name='helpbtnparent', parent=parent, align=uiconst.TOTOP, padTop=8)
        Button(name='helpChannelButton', parent=helpbtnparent, label=localization.GetByLabel('UI/Help/JoinChannel'), func=self.JoinHelpChannel, btn_default=0, align=uiconst.TOPRIGHT)

    def _LoadSupportPetitions(self, parent):
        petpar = ContainerAutoSize(name='petitionpar', parent=parent, align=uiconst.TOTOP, padTop=8)
        petbtnparent = ContainerAutoSize(name='petbtnparent', parent=parent, align=uiconst.TOTOP, padTop=8)
        petitioner = sm.RemoteSvc('petitioner')
        if petitioner.IsZendeskSwapEnabled():
            EveLabelMedium(name='helpCenterDescriptionLabel', text=localization.GetByLabel('UI/Help/HelpCenterDescription'), parent=petpar, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
            if petitioner.HasOpenTickets():
                EveLabelMedium(name='openOldPetitionsLinkLabel', text=localization.GetByLabel('UI/Help/OpenOldPetitions'), parent=petpar, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
            Button(name='openHelpCenterButton', parent=petbtnparent, label=localization.GetByLabel('UI/Help/OpenHelpCenterFinal'), func=self.OpenHelpCenter, btn_default=0, align=uiconst.TOPRIGHT, uniqueUiName=pConst.UNIQUE_NAME_HELP_CENTER_BTN)
        else:
            EveLabelMedium(name='openPetitionsLabelOld', text=localization.GetByLabel('UI/Help/OpenPetitions'), parent=petpar, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
            Button(name='filePetitionButton', parent=petbtnparent, label=localization.GetByLabel('UI/Help/FilePetition'), func=self.FilePetition, btn_default=0, align=uiconst.TOPRIGHT)
            if petitioner.IsZendeskEnabled() and session.languageID.lower() == 'en':
                Button(name='openHelpCenterButton', parent=petbtnparent, label=localization.GetByLabel('UI/Help/OpenHelpCenter'), func=self.OpenHelpCenter, btn_default=0, align=uiconst.TOPRIGHT, uniqueUiName=pConst.UNIQUE_NAME_HELP_CENTER_BTN, top=Button.default_height + 4)

    def _LoadSupportBugReport(self, parent):
        EveLabelMedium(name='reportBugLabel', text=localization.GetByLabel('UI/Help/ReportBugFull'), parent=parent, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
        bugreportbtnparent = ContainerAutoSize(name='bugreportbtnparent', parent=parent, align=uiconst.TOTOP, padTop=8)
        Button(name='reportBugButton', parent=bugreportbtnparent, label=localization.GetByLabel('UI/Help/ReportBug'), func=self.CreateBugReport, align=uiconst.TOPRIGHT)

    def ConstructContent(self):
        self._LoadSupportHelpChannel(self.mainCont)
        LineThemeColored(name='line1', parent=self.mainCont, align=uiconst.TOTOP, padTop=8)
        self._LoadSupportPetitions(self.mainCont)
        if ShouldShowBugreportButton(sm.GetService('machoNet')):
            LineThemeColored(name='line3', parent=self.mainCont, align=uiconst.TOTOP, padTop=8)
            self._LoadSupportBugReport(self.mainCont)

    def _OnMainContAutoSized(self):
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetFixedHeight(height)

    def OpenHelpCenter(self, *args):
        import webbrowser
        if uicore.Message('HelpCenterOpenWarning', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            petitioner = sm.RemoteSvc('petitioner')
            webbrowser.open_new(petitioner.GetZendeskJwtLink())

    def FilePetition(self, *args):
        sm.GetService('petition').NewPetition()

    def JoinHelpChannel(self, *etc):
        normal_help_channel = GetChatService().XmppChatMgr.GetHelpChannel()
        if normal_help_channel:
            wnd = GetChatService().GetGroupChatWindow(normal_help_channel)
            if wnd and not wnd.destroyed:
                wnd.Maximize()
                return
        GetChatService().JoinHelpChannels()

    def OnWndMouseDown(self, *args):
        sm.GetService('neocom').BlinkOff('help')

    def _OnClose(self, *args):
        if getattr(self, 'sr', None) and self.sr.Get('form', None):
            self.sr.form.Close()
