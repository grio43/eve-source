#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\depletionPinManager.py
import carbonui.const as uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.common.lib import appConst as const

class DepletionManager(Window):
    __guid__ = 'form.DepletionManager'
    default_windowID = 'depletionManager'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.selected = None
        self.SetCaption('Depletion Manager')
        self.SetMinSize([280, 500])
        headerContainer = Container(name='headerParent', parent=self.sr.main, align=uiconst.TOTOP, height=100, padding=(2, 2, 2, 2))
        text = "This gives you a list of depletion\npoints that you've placed on the planet.\nYou can edit some aspects of these points\n    * amount - is the base extraction amount\n    * duration - is the in minutes and tells how many times the program will be resubmitted\n    * headRadius - tells the size of the head\n        "
        eveLabel.EveLabelMedium(parent=headerContainer, text=text, align=uiconst.TOALL)
        timeContainer = Container(name='timeParent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=40)
        editContainer = Container(name='editParent', parent=self.sr.main, align=uiconst.TOBOTTOM, top=20, height=50, padTop=12)
        scrollContainer = Container(name='scrollParent', parent=self.sr.main, align=uiconst.TOALL)
        self.depletionPointScroll = eveScroll.Scroll(parent=scrollContainer, align=uiconst.TOALL, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.depletionPointScroll.multiSelect = 0
        self.pinManager = attributes.get('pinManager', None)
        amountContainer = Container(name='amountParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        durationContainer = Container(name='durationParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        headRadiusContainer = Container(name='headRadiusParent', parent=editContainer, align=uiconst.TOLEFT, width=90)
        self.amountEdit = SingleLineEditInteger(name='amount', parent=amountContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), label='amount', OnReturn=self.OnAmountSubmit)
        self.amountEdit.OnFocusLost = self.OnAmountSubmit
        self.durationEdit = SingleLineEditInteger(name='duration', parent=durationContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), label='duration', OnReturn=self.OnDurationSubmit)
        self.durationEdit.OnFocusLost = self.OnDurationSubmit
        self.headRadiusEdit = SingleLineEditFloat(name='headRadius', parent=headRadiusContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), label='headRadius', OnReturn=self.OnHeadRadiusSubmit)
        self.headRadiusEdit.OnFocusLost = self.OnHeadRadiusSubmit
        self.timeEdit = SingleLineEditInteger(name='timeEdit', parent=timeContainer, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         1,
         80,
         0), label='Time in days', setvalue='14')
        self.LoadDepletionPointScroll()
        self.sr.saveDeleteButtons = ButtonGroup(btns=[['Submit', self.Submit, ()]], parent=self.sr.main, idx=0)

    def LoadDepletionPointScroll(self):
        scrolllist = []
        for point in self.pinManager.depletionPoints:
            scrolllist.append(GetFromClass(Generic, {'label': '%d<t>%d<t>%d<t>%.3f' % (point.index,
                       point.GetAmount(),
                       point.GetDuration(),
                       point.GetHeadRadius()),
             'index': point.index,
             'OnClick': self.OnDepletionPointClicked}))

        self.depletionPointScroll.Load(contentList=scrolllist, headers=['index',
         'amount',
         'duration',
         'headRadius'])

    def Submit(self):
        totalDuration = int(self.timeEdit.GetValue()) * const.DAY
        self.pinManager.GMRunDepletionSim(totalDuration)

    def OnDepletionPointClicked(self, entry):
        index = entry.sr.node.index
        self.selected = index
        depletionPoint = self.pinManager.depletionPoints[index]
        duration = depletionPoint.GetDuration()
        amount = depletionPoint.GetAmount()
        headRadius = depletionPoint.GetHeadRadius()
        self.amountEdit.SetValue(str(amount))
        self.durationEdit.SetValue(str(duration))
        self.headRadiusEdit.SetValue(str(headRadius))
        for i, depletionPoint in enumerate(self.pinManager.depletionPoints):
            if i == index:
                depletionPoint.drillArea.pinColor = Color.GREEN
            else:
                depletionPoint.drillArea.pinColor = Color.YELLOW

    def GetSelectedDepletionPoint(self):
        if self.selected is None:
            return
        return self.pinManager.depletionPoints[self.selected]

    def OnAmountSubmit(self, *args):
        if not self or self.destroyed:
            return
        newAmount = int(self.amountEdit.GetValue())
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        depletionPoint.amount = newAmount
        self.LoadDepletionPointScroll()

    def OnDurationSubmit(self, *args):
        if not self or self.destroyed:
            return
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        newDuration = int(self.durationEdit.GetValue())
        depletionPoint.duration = newDuration
        self.LoadDepletionPointScroll()

    def OnHeadRadiusSubmit(self, *args):
        if not self or self.destroyed:
            return
        depletionPoint = self.GetSelectedDepletionPoint()
        if depletionPoint is None:
            return
        newHeadRadius = float(self.headRadiusEdit.GetValue())
        depletionPoint.headRadius = newHeadRadius
        depletionPoint.drillArea.pinRadius = newHeadRadius
        self.LoadDepletionPointScroll()

    def _OnClose(self, *args):
        for depletionPoint in self.pinManager.depletionPoints:
            depletionPoint.drillArea.pinColor = Color.YELLOW
