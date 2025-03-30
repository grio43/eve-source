#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\dotWeapons.py
import eveformat
import gametime
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbon.common.script.util.format import FmtDate, FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.button import Button
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scroll import Scroll
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
import carbonui
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
BG_COLOR = (0.1, 0.1, 0.1, 0.5)

class DotWeaponWnd(Window):
    default_minSize = (450, 500)
    default_windowID = 'dotWeaponWnd'
    default_caption = 'Damage Over Time Weapons'

    def ApplyAttributes(self, attributes):
        super(DotWeaponWnd, self).ApplyAttributes(attributes)
        self.ConstructUI()

    def ConstructUI(self):
        cont = Container(parent=self.content, align=carbonui.Align.TOTOP, bgColor=BG_COLOR, height=50)
        runBtn = Button(parent=cont, align=carbonui.Align.CENTERTOP, func=self.RunThread, label='Run Thread', left=-50)
        stopBtn = Button(parent=cont, align=carbonui.Align.CENTERTOP, func=self.StopThread, label='Stop Thread', left=50)
        self.threadStateLabel = carbonui.TextBody(parent=cont, text='', align=carbonui.Align.CENTERBOTTOM)
        leftCont = Container(parent=self.content, align=carbonui.Align.TOLEFT, width=250)
        cont = Container(parent=leftCont, align=carbonui.Align.TOTOP, height=40, bgColor=BG_COLOR, top=40)
        carbonui.TextBody(parent=cont, text='targetID', align=carbonui.Align.CENTERLEFT)
        editLeft = 70
        self.targetIdEdit = SingleLineEditText(name='targetIdEdit', parent=cont, align=carbonui.Align.CENTERLEFT, left=editLeft, setvalue=unicode(session.shipid))
        cont = Container(parent=leftCont, align=carbonui.Align.TOTOP, height=40, bgColor=BG_COLOR)
        carbonui.TextBody(parent=cont, text='duration', align=carbonui.Align.CENTERLEFT)
        self.durationEdit = SingleLineEditText(name='durationEdit', parent=cont, align=carbonui.Align.CENTERLEFT, left=editLeft, hintText='(in seconds)', setvalue='40')
        cont = Container(parent=leftCont, align=carbonui.Align.TOTOP, height=40, bgColor=BG_COLOR)
        carbonui.TextBody(parent=cont, text='MAX DAMAGE', align=carbonui.Align.CENTERLEFT)
        self.maxDamageEdit = SingleLineEditText(parent=cont, align=carbonui.Align.CENTERLEFT, left=editLeft, setvalue='5000')
        cont = Container(parent=leftCont, align=carbonui.Align.TOTOP, height=40, bgColor=BG_COLOR)
        carbonui.TextBody(parent=cont, text='MAX % HP', align=carbonui.Align.CENTERLEFT)
        self.maxHpPercentageEdit = SingleLineEditText(parent=cont, align=carbonui.Align.CENTERLEFT, left=editLeft, setvalue='0.01', hintText='in range 0-100')
        cont = Container(parent=leftCont, align=carbonui.Align.TOTOP, height=40, bgColor=BG_COLOR)
        applyButton = Button(parent=cont, align=carbonui.Align.CENTERBOTTOM, func=self.ApplyDamage, label='Apply')
        restCont = Container(parent=self.content, align=carbonui.Align.TOALL, top=40, bgColor=BG_COLOR)
        viewCurrent = Button(parent=restCont, align=carbonui.Align.CENTERTOP, func=self.LoadDotDamage, label='View Current DOT Damage')
        self.scroll = Scroll(parent=restCont, top=30)
        uthread2.StartTasklet(self.LoadDotDamage)
        uthread2.StartTasklet(self.UpdateThreadStateLabel)

    def GetMenuMoreOptions(self):
        menu_data = super(DotWeaponWnd, self).GetMenuMoreOptions()
        if session.role & ROLE_PROGRAMMER:
            menu_data.AddEntry('QA Reload', self.DebugReload)
        return menu_data

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyDamage(self, *args):
        targetID = int(self.targetIdEdit.GetValue())
        duration = int(self.durationEdit.GetValue())
        maxDamage = int(self.maxDamageEdit.GetValue())
        maxPercentage = float(self.maxHpPercentageEdit.GetValue())
        slashText = 'dotWeapons apply %s %s %s %s' % (targetID,
         duration,
         maxDamage,
         maxPercentage)
        sm.GetService('slash').SlashCmd(slashText)
        self.LoadDotDamage()

    def LoadDotDamage(self, *args):
        slashText = 'dotWeapons viewcurrent'
        currentDotWeapons = sm.GetService('slash').SlashCmd(slashText)
        scrollList = []
        for targetInfo in currentDotWeapons:
            targetID = targetInfo.targetID
            entry = GetFromClass(ListGroup, {'GetSubContent': self.GetDotWeaponSubContent,
             'label': targetID,
             'groupItems': targetInfo.dotApplications,
             'id': ('dotDamage', targetID),
             'showicon': 'hide',
             'state': 'locked',
             'BlockOpenWindow': 1,
             'selectable': 0,
             'MenuFunction': self.GetTargetMenu,
             'targetID': targetID})
            scrollList.append(entry)

        headers = ['duration',
         'timeLeft',
         'maxDamage',
         'maxHp%',
         'added',
         'expires']
        self.scroll.Load(contentList=scrollList, headers=headers, noContentHint='nothing to show')

    def GetTargetMenu(self, node):
        targetID = node.targetID
        m = MenuData()
        m.AddEntry('Clear all dotApplications', func=lambda : self.ClearDotApplications(targetID))
        return m

    def ClearDotApplications(self, targetID):
        slashText = 'dotWeapons clear %s ' % targetID
        sm.GetService('slash').SlashCmd(slashText)
        self.LoadDotDamage()

    def GetDotWeaponSubContent(self, nodedata, *args):
        scrollList = []
        groupItems = nodedata.groupItems
        for dotApplications in groupItems:
            entry = GetFromClass(DotWeaponEntry, {'dotApplications': dotApplications,
             'label': ' '})
            scrollList.append(entry)

        return scrollList

    def RunThread(self, *args):
        slashText = 'dotWeapons runthread'
        sm.GetService('slash').SlashCmd(slashText)
        self.LoadDotDamage()
        self.UpdateThreadStateLabel()

    def StopThread(self, *args):
        slashText = 'dotWeapons stopthread'
        sm.GetService('slash').SlashCmd(slashText)
        self.LoadDotDamage()
        self.UpdateThreadStateLabel()

    def UpdateThreadStateLabel(self):
        slashText = 'dotWeapons threadstate'
        threadState = sm.GetService('slash').SlashCmd(slashText)
        if threadState:
            text = eveformat.color('Thread is running', eveColor.SUCCESS_GREEN_HEX)
        else:
            text = eveformat.color('Thread is NOT running', eveColor.DANGER_RED_HEX)
        self.threadStateLabel.text = text


class DotWeaponEntry(Generic):

    def ApplyAttributes(self, attributes):
        super(DotWeaponEntry, self).ApplyAttributes(attributes)
        self.updatingThread = None

    def Load(self, node):
        if self.destroyed:
            self.updatingThread = None
            return
        dotApplications = node.dotApplications
        textList = [FmtAmt(dotApplications.duration / const.SEC)]
        timeLeft = dotApplications.expiryTime - gametime.GetSimTime()
        if timeLeft > 0:
            textList.append(FmtDate(timeLeft, 'ss'))
        else:
            textList.append('Expired')
        textList += ['-' if dotApplications.maxDamage is None else FmtAmt(dotApplications.maxDamage),
         '-' if dotApplications.maxHpPercentage is None else FmtAmt(dotApplications.maxHpPercentage, showFraction=2),
         FmtDate(dotApplications.addedTimestamp),
         FmtDate(dotApplications.expiryTime)]
        node.label = '<t>'.join(textList)
        super(DotWeaponEntry, self).Load(node)
        if not self.updatingThread:
            self.updatingThread = AutoTimer(500, self.Load, node)
