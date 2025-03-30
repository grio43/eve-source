#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\surveyClaimWnd.py
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui import uiconst
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium
from localization import GetByLabel, GetByMessageID
from surveys import GetSurveyByID

class ClaimSurveyRewardsWnd(Window):
    default_width = 400
    default_height = 200
    default_windowID = 'claimSurveyRewardsWnd'

    def ApplyAttributes(self, attributes):
        attributes.useDefaultPos = True
        super(ClaimSurveyRewardsWnd, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.sr.headerParent.display = False
        self.HideHeaderButtons()
        surveyIDS = attributes.surveyIDs
        text = self.GetSurveyText(surveyIDS)
        cont = Container(name='innerCont', parent=self.sr.main, align=uiconst.TOALL, padding=(25, 25, 25, 0))
        headerLabel = Label(parent=cont, fontsize=18, text='<center>%s</center>' % GetByLabel('UI/Surveys/SurveyRewards'), align=uiconst.TOTOP, uppercase=True, padBottom=13)
        textLabel = EveLabelMedium(parent=cont, text=text, align=uiconst.TOTOP, padBottom=13)
        claimBtn = Button(parent=self.sr.main, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/LoginRewards/ClaimButtonText'), func=self.OnClaimBtnClicked, top=20)
        contentHeight = self.sr.headerParent.height + cont.padTop + headerLabel.height + headerLabel.padBottom + textLabel.height + textLabel.padBottom + claimBtn.height + claimBtn.top
        self.height = max(self.height, contentHeight)

    def GetSurveyText(self, surveyIDs):
        text = GetByLabel('UI/Surveys/ClaimMessages/GenericClaimSurveyRewards')
        if len(surveyIDs) > 1:
            return text
        surveyID = surveyIDs.pop()
        survey = GetSurveyByID(surveyID)
        if survey and survey.GetClaimLabelID():
            return GetByMessageID(survey.GetClaimLabelID())
        return text

    def CloseByUser(self, *args):
        self.SetModalResult(uiconst.ID_CLOSE)
        super(ClaimSurveyRewardsWnd, self).CloseByUser(*args)

    def OnClaimBtnClicked(self, *args, **kwargs):
        self.SetModalResult(uiconst.ID_YES)
