#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corpVotingWindow.py
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import CorpVotes
from localization import GetByLabel

class CorpVotingWindow(Window):
    default_name = 'corpVotingWindow'
    default_minSize = [256, 256]
    default_iconNum = None

    def ApplyAttributes(self, attributes):
        super(CorpVotingWindow, self).ApplyAttributes(attributes)
        self.corpID = attributes.corpID
        self.windowID = '%s_%d' % (self.default_name, self.corpID)
        self.SetCaption(GetByLabel('UI/Corporations/BaseCorporationUI/VoteWindowCaption', corporationName=cfg.eveowners.Get(self.corpID).name))
        self.ConstructLayout()

    def ConstructLayout(self):
        self.main = self.GetMainArea()
        self.corpVotesPanel = CorpVotes(parent=self.main, corpID=self.corpID)
        self.corpVotesPanel.Load(None)
