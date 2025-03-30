#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\extras\tourneyBanUI.py
import evetypes
import carbonui.const as uiconst
import blue
from carbon.common.script.util import timerstuff
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from eve.common.lib import appConst as const
from carbonui.control.button import Button

class TourneyBanUI(Window):
    __guid__ = 'form.TourneyBanUI'
    default_alwaysLoadDefaults = True

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption('Tournament Ban Prompt')
        self.SetMinSize((300, 375))

    def SetModalResult(self, result, caller = None):
        if result == uiconst.ID_OK:
            return
        super(TourneyBanUI, self).SetModalResult(result, caller)

    def Execute(self, banID, numBans, curBans, deadline, respondToNodeID, shipList):
        self.banID = banID
        self.deadline = deadline
        self.respondToNodeID = respondToNodeID
        self.resetButton = Button(label='Submit Ban' if numBans > 0 else 'Okay', parent=self.sr.main, align=uiconst.TOBOTTOM, func=self.Submit, state=uiconst.UI_NORMAL, padding=5)
        eveLabel.EveLabelLarge(text="Let's ban some ships!" if numBans > 0 else "Here's the bans:", parent=self.sr.main, align=uiconst.TOTOP, top=10, padding=5, color=(0.5, 0.5, 1, 1))
        eveLabel.Label(text='You have banned:', parent=self.sr.main, align=uiconst.TOTOP, top=5, padding=5)
        eveLabel.Label(text='<br>'.join([ evetypes.GetName(typeID) for typeID in curBans[0] ]), padding=5, parent=self.sr.main, align=uiconst.TOTOP)
        eveLabel.Label(text='They have banned:', parent=self.sr.main, align=uiconst.TOTOP, top=5, padding=5)
        eveLabel.Label(text='<br>'.join([ evetypes.GetName(typeID) for typeID in curBans[1] ]), padding=5, parent=self.sr.main, align=uiconst.TOTOP)
        ships = []
        for typeID in evetypes.GetTypeIDsByCategory(const.categoryShip):
            if typeID in [ tup[1] for tup in shipList ]:
                if evetypes.IsPublished(typeID):
                    name = evetypes.GetName(typeID)
                    if not name.startswith('[no messageID:'):
                        ships.append((name, typeID))

        banOptions = [('Pass', -1)] + sorted(ships)
        self.banChoices = []
        for banNum in xrange(numBans):
            self.banChoices.append(Combo(label='Ban: ', parent=self.sr.main, options=banOptions, top=20, padding=5, align=uiconst.TOTOP))

        if numBans > 0:
            banCont = Container(name='banTimer', parent=self.sr.main, align=uiconst.TOTOP, height=50)
            self.countdownText = eveLabel.Label(parent=banCont, align=uiconst.CENTER, fontsize=36, color=(1, 0, 0, 1))
            self.countdownTimer = timerstuff.AutoTimer(100, self.UpdateTimer)
        uicore.registry.SetFocus(self)
        self.MakeUnKillable()

    def Submit(self, *args):
        machoNet = sm.GetService('machoNet')
        remoteTourneyMgr = machoNet.ConnectToRemoteService('tourneyMgr', self.respondToNodeID)
        banTypes = []
        for choice in self.banChoices:
            shipTypeToBan = choice.GetValue()
            if shipTypeToBan != -1:
                banTypes.append(shipTypeToBan)

        remoteTourneyMgr.BanShip(self.banID, banTypes)
        self.Close()

    def UpdateTimer(self):
        timeDiffMS = max(0, blue.os.TimeDiffInMs(blue.os.GetWallclockTime(), self.deadline))
        self.countdownText.text = '%.1f' % (float(timeDiffMS) / 1000.0,)
        if timeDiffMS == 0:
            self.MakeKillable()
            self.countdownTimer = None
