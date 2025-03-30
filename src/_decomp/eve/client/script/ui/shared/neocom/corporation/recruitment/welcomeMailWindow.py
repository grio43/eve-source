#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\recruitment\welcomeMailWindow.py
import localization
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from carbonui.fontconst import EVE_SMALL_FONTSIZE
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.util import uix

class WelcomeMailWindow(Window):
    __notifyevents__ = ['OnCorporationWelcomeMailChanged']
    default_width = 500
    default_height = 400

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.EditWelcomeMail()
        self.SetCaption(localization.GetByLabel('UI/Corporations/Applications/CorpWelcomeMail'))

    def EditWelcomeMail(self, *args):
        welcomeMail = sm.GetService('corp').GetCorpWelcomeMail()
        self.confirmButtonGroup = ButtonGroup(btns=[(localization.GetByLabel('UI/Generic/Apply'),
          self.SaveWelcomeMail,
          (),
          84)], parent=self.sr.main)
        lastEditBy = ''
        labelHeight = uix.GetTextHeight('gX', fontsize=EVE_SMALL_FONTSIZE)
        self.welcomeMailEditLabel = eveLabel.EveLabelSmall(parent=self.sr.main, text=lastEditBy, align=uiconst.TOBOTTOM, height=labelHeight, padding=const.defaultPadding)
        if welcomeMail.characterID is not None:
            lastEditBy = localization.GetByLabel('UI/Corporations/Applications/WelcomeMailLastEdit', characterName=cfg.eveowners.Get(welcomeMail.characterID).name, changeDate=welcomeMail.changeDate)
            self.welcomeMailEditLabel.text = lastEditBy
            self.welcomeMailEditLabel.display = True
        else:
            self.welcomeMailEditLabel.display = False
        self.welcomeMailContentContainer = EditPlainText(parent=self.sr.main, align=uiconst.TOALL, showattributepanel=1, padding=const.defaultPadding, maxLength=const.mailMaxTaggedBodySize)
        self.welcomeMailContentContainer.SetValue(welcomeMail.welcomeMail)

    def SaveWelcomeMail(self, *args):
        welcomeMail = sm.GetService('corp').GetCorpWelcomeMail()
        newWelcomeMail = self.welcomeMailContentContainer.GetValue()
        if newWelcomeMail != welcomeMail.welcomeMail:
            sm.GetService('corp').SetCorpWelcomeMail(newWelcomeMail)

    def OnCorporationWelcomeMailChanged(self, characterID, changeDate):
        self.UpdateWelcomeMail(characterID, changeDate)

    def UpdateWelcomeMail(self, characterID, changeDate):
        if getattr(self, 'welcomeMailEditLabel', None) is not None:
            if self.welcomeMailEditLabel.display == False:
                self.welcomeMailEditLabel.display = True
                uicore.animations.MorphScalar(self.welcomeMailEditLabel, 'height', startVal=0, endVal=12, duration=1.0)
            uicore.animations.FadeOut(self.welcomeMailEditLabel, duration=1.0, sleep=True)
            self.welcomeMailEditLabel.text = localization.GetByLabel('UI/Corporations/Applications/WelcomeMailLastEdit', characterName=cfg.eveowners.Get(characterID).name, changeDate=changeDate)
            if characterID == session.charid:
                color = Color(0.0, 1.0, 0.0, 0.0).GetRGBA()
            else:
                color = Color(1.0, 0.0, 0.0, 0.0).GetRGBA()
            self.welcomeMailEditLabel.color = color
            uicore.animations.FadeIn(self.welcomeMailEditLabel, endVal=1.0, duration=1.0)
