#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\storylineAgentContentCard.py
import uthread
from carbonui import uiconst
from eve.client.script.ui.control.eveLabel import EveHeaderLarge
from eve.client.script.ui.shared.agencyNew.ui.contentCards.agentContentCard import AgentContentCard
import blue

class StorylineAgentContentCard(AgentContentCard):
    default_name = 'StorylineAgentContentCard'
    default_padBottom = 46

    def ApplyAttributes(self, attributes):
        super(StorylineAgentContentCard, self).ApplyAttributes(attributes)
        self.expiryLabel = EveHeaderLarge(name='expiryLabel', parent=self, align=uiconst.CENTERBOTTOM, top=-24)
        uthread.new(self.UpdateExpiryLabelThread)

    def UpdateExpiryLabelThread(self):
        while not self.destroyed:
            self.expiryLabel.SetText(self.contentPiece.GetExpiryTimeText())
            blue.synchro.SleepWallclock(100)
