#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\implant.py
import blue
import evetypes
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FmtTimeInterval
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.common.lib import appConst as const
from menu import MenuLabel

class ImplantEntry(SE_BaseClassCore):
    __guid__ = 'listentry.ImplantEntry'
    __params__ = ['label']

    def Startup(self, *etc):
        self.sr.label = EveLabelMedium(text='', parent=self, left=32, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.sr.timeLabel = EveLabelMedium(text='', parent=self, left=18, top=2, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMRIGHT)
        self.sr.icon = Icon(icon='ui_22_32_30', parent=self, size=32, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED)
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo

    def Load(self, node):
        self.sr.node = node
        data = node
        sublevel = node.sublevel or 0
        if evetypes.GetGroupID(self.sr.node.implant_booster.typeID) == const.groupBooster:
            slot = getattr(sm.GetService('godma').GetType(node.implant_booster.typeID), 'boosterness', None)
            timeToEnd = node.implant_booster.expiryTime
        else:
            slot = getattr(sm.GetService('godma').GetType(node.implant_booster.typeID), 'implantness', None)
            timeToEnd = None
        if slot is None:
            self.sr.label.text = data.label
        else:
            self.sr.label.text = localization.GetByLabel('UI/Control/Entries/ImplantLabel', implantName=data.label, slotNum=int(slot))
        self.sr.icon.LoadIcon(evetypes.GetIconID(node.implant_booster.typeID), ignoreSize=True)
        self.sr.icon.SetSize(32, 32)
        if timeToEnd is not None:
            self.UpdateTime(timeToEnd)
            self.sr.timeOutTimer = AutoTimer(1000, self.UpdateTime, timeToEnd)
        else:
            self.sr.timeLabel.text = ''
            self.sr.timeOutTimer = None
        offset = sublevel * 16
        self.sr.icon.left = offset
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width

    def UpdateTime(self, timeToEnd):
        timeInterval = timeToEnd - blue.os.GetWallclockTime()
        if timeInterval > const.MONTH30:
            timeBreakAt = 'hour'
        elif timeInterval > const.DAY:
            timeBreakAt = 'min'
        else:
            timeBreakAt = 'sec'
        self.sr.timeLabel.text = FmtTimeInterval(timeInterval, timeBreakAt)

    def GetMenu(self):
        m = [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
        if not evetypes.GetGroupID(self.sr.node.implant_booster.typeID) == const.groupBooster and getattr(self.sr.node.implant_booster, 'itemID', None):
            m.append((MenuLabel('UI/Control/Entries/ImplantUnplug'), self.RemoveImplant, (self.sr.node.implant_booster.itemID, self.sr.node.implant_booster.typeID)))
        return m

    def OnDblClick(self, *args):
        self.ShowInfo()

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.sr.node.implant_booster.typeID, getattr(self.sr.node.implant_booster, 'itemID', None))

    def RemoveImplant(self, itemID, typeID):
        implantLink = GetShowInfoLink(typeID, evetypes.GetName(typeID), itemID)
        if eve.Message('ConfirmUnPlugInImplant', {'implantLink': implantLink}, uiconst.OKCANCEL) == uiconst.ID_OK:
            PlaySound(uiconst.SOUND_REMOVE)
            sm.GetService('godma').GetDogmaLM().DestroyImplant(itemID)

    def GetDynamicHeight(self, width):
        text = localization.GetByLabel('UI/Control/Entries/ImplantLabel', implantName=self.label, slotNum=0)
        _, textHeight = EveLabelMedium.MeasureTextSize(text)
        return max(32, textHeight + const.defaultPadding)
