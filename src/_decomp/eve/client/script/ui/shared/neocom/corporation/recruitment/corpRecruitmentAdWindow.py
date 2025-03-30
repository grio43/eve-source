#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\recruitment\corpRecruitmentAdWindow.py
import localization
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.corporation.recruitment.recruitmentEntry import RecruitmentEntry

class CorpRecruitmentAdStandaloneWindow(Window):
    default_width = 500
    default_height = 400

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        data = attributes.data
        if data.corporationID != session.corpid:
            buttons = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Recruitment/ApplyToJoinCorporation'),
              self.ApplyToCorp,
              (data.corporationID,),
              81]]
            ButtonGroup(btns=buttons, parent=self.sr.main, idx=0)
        self.scroll = eveScroll.Scroll(parent=self.sr.main, name='scroll')
        self.scroll.RemoveActiveFrame()
        self.scroll.HideBackground()
        self.SetCaption('%s - %s' % (cfg.eveowners.Get(data.corporationID).name, data.adTitle))
        self.ModifyDataForThisWindow(data)
        entry = GetFromClass(RecruitmentEntry, data)
        self.scroll.Load(contentList=[entry])

    def ModifyDataForThisWindow(self, data):
        data.corpView = False
        data.standaloneMode = True
        data.searchMask = None
        data.searchLangMask = None
        data.grade = None
        data.expandedView = True
        if getattr(data, 'recruiters', None) is None:
            data.recruiters = sm.GetService('corp').GetRecruiters(data.advert.adID)

    def ApplyToCorp(self, corpID):
        sm.GetService('corp').ApplyForMembership(corpID)
