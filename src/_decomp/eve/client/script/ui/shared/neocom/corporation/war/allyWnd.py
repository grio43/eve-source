#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\allyWnd.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.corporation.war.warAllyEntry import AllyListEntry
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from localization import GetByLabel
import blue

class AllyWnd(Window):
    __guid__ = 'form.AllyWnd'
    __notifyevents__ = []
    default_windowID = 'AllyWnd'
    default_width = 350
    default_height = 282
    default_minSize = (default_width, default_height)
    default_iconNum = 'res:/ui/Texture/WindowIcons/mercenary.png'

    def __init__(self, **kwargs):
        self.war = None
        self.allies = None
        self.allyScroll = None
        super(AllyWnd, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.war = attributes.war
        self.allies = attributes.allies
        self.SetCaption(GetByLabel('UI/Corporations/Wars/Allies'))
        self.ConstructLayout()

    def ConstructLayout(self):
        topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=48, padding=const.defaultPadding)
        alliesCont = Container(name='alliesCont', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         0,
         const.defaultPadding))
        allyIcon = Sprite(parent=topCont, align=uiconst.TOPLEFT, pos=(0, 0, 46, 46), texturePath='res:/UI/Texture/Icons/Mercenary_64.png')
        EveCaptionSmall(text=GetByLabel('UI/Corporations/Wars/Allies'), parent=topCont, align=uiconst.TOTOP, height=22, padLeft=46, top=3)
        subTitle = EveLabelMedium(text='', parent=topCont, align=uiconst.TOTOP, padLeft=46)
        defenderName = cfg.eveowners.Get(self.war.declaredByID).name
        subTitle.text = GetByLabel('UI/Corporations/Wars/InWarAgainst', defenderName=defenderName)
        self.allyScroll = Scroll(name='alliesScroll', parent=alliesCont, align=uiconst.TOALL)
        self.GetAllies()

    def IsOpenForAllies(self):
        return self.war.openForAllies

    def GetAllies(self):
        if self.allies is None:
            warStatMon = eveMoniker.GetWarStatistic(self.war.warID)
            warStatMon.Bind()
            baseInfo = warStatMon.GetBaseInfo()
            self.allies = baseInfo[-1]
        try:
            allies = self.allies.itervalues()
        except AttributeError:
            allies = self.allies

        currentTime = blue.os.GetWallclockTime()
        scrollList = [ GetFromClass(AllyListEntry, {'warID': self.war.warID,
         'allyID': ally.allyID,
         'warNegotiationID': None,
         'allyRow': ally,
         'isAlly': True,
         'originalWarTimeStarted': self.war.timeStarted,
         'originalWarTimeFinished': self.war.timeStarted}) for ally in allies if currentTime <= ally.timeFinished ]
        self.allyScroll.Load(contentList=scrollList, noContentHint=GetByLabel('UI/Corporations/Wars/NoAlliesInWar'))
