#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\siphonBracket.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
import localization
import carbonui.const as uiconst

class SiphonSiloBracket(InSpaceBracket):

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.width = 32
        self.height = 40
        container = Container(parent=self, align=uiconst.BOTTOMLEFT, height=8, width=32)
        inner = Container(parent=container, padding=(2, 2, 2, 2))
        self.frame = Frame(parent=container)
        container.fill = Fill(parent=inner, align=uiconst.TOLEFT_PROP, width=0, padding=(0, 0, 0, 0))
        self.capacityBar = container

    def Startup(self, slimItem, ball = None, transform = None):
        InSpaceBracket.Startup(self, slimItem, ball=ball, transform=transform)

    def SetHint(self, hint):
        self.capacityBar.hint = hint
        self.hint = hint

    def SetCapacityBarPercentage(self, capacityusage):
        usage = min(float(capacityusage.used) / float(capacityusage.capacity), 1.0)
        self.capacityBar.fill.width = usage
        if usage > 0.98:
            self.capacityBar.fill.color = Color.YELLOW
        else:
            self.capacityBar.fill.color = Color.GRAY
        self.SetHint(localization.GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=capacityusage.used, capacity=capacityusage.capacity))

    def GetSiphonCapacityUsage(self):
        ballpark = sm.GetService('michelle').GetRemotePark()
        capacity = ballpark.GetCapacityOfSiphon(self.slimItem.itemID)
        return capacity

    def Select(self, status):
        InSpaceBracket.Select(self, status)
        if status:
            self.SetCapacityBarPercentage(self.GetSiphonCapacityUsage())
            self.capacityBar.state = uiconst.UI_NORMAL
        else:
            self.capacityBar.state = uiconst.UI_HIDDEN
            self.SetHint('')
