#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\levelSelector.py
import appConst
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uicore import uicore
from eve.client.script.parklife import states
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon

class StandingLevelSelector(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.level = attributes.get('level', None)
        self.iconPadding = attributes.get('iconPadding', 6)
        self.vertical = attributes.get('vertical', False)
        if attributes.get('callback', None):
            self.OnStandingLevelSelected = attributes.get('callback', None)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.standingList = {appConst.contactHighStanding: localization.GetByLabel('UI/PeopleAndPlaces/ExcellentStanding'),
         appConst.contactGoodStanding: localization.GetByLabel('UI/PeopleAndPlaces/GoodStanding'),
         appConst.contactNeutralStanding: localization.GetByLabel('UI/PeopleAndPlaces/NeutralStanding'),
         appConst.contactBadStanding: localization.GetByLabel('UI/PeopleAndPlaces/BadStanding'),
         appConst.contactHorribleStanding: localization.GetByLabel('UI/PeopleAndPlaces/TerribleStanding')}
        levelList = self.standingList.keys()
        levelList.sort()
        shift = 20 + self.iconPadding
        for i, relationshipLevel in enumerate(levelList):
            leftPos = i * shift * float(not self.vertical)
            rightPos = i * shift * float(self.vertical)
            contName = 'level%d' % i
            level = StandingsContainer(name=contName, parent=self, align=uiconst.TOPLEFT, pos=(leftPos,
             rightPos,
             20,
             20), level=relationshipLevel, text=self.standingList.get(relationshipLevel), windowName='contactmanagement')
            setattr(self.sr, contName, level)
            level.OnClick = (self.LevelOnClick, relationshipLevel, level)
            if self.level == relationshipLevel:
                level.sr.selected.state = uiconst.UI_DISABLED
                uicore.registry.SetFocus(level)

    def LevelOnClick(self, level, container, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        for i in xrange(0, 5):
            cont = self.sr.Get('level%d' % i)
            cont.sr.selected.state = uiconst.UI_HIDDEN

        container.sr.selected.state = uiconst.UI_DISABLED
        self.level = level
        if hasattr(self, 'OnStandingLevelSelected'):
            self.OnStandingLevelSelected(level)

    def GetValue(self):
        return self.level


class StandingsContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', '')
        self.text = text
        level = attributes.get('level', None)
        self.level = level
        windowName = attributes.get('windowName', '')
        self.windowName = windowName
        self.Prepare_(text, level)
        self.cursor = uiconst.UICURSOR_SELECT

    def Prepare_(self, text = '', contactLevel = None, *args):
        self.isTabStop = 1
        self.state = uiconst.UI_NORMAL
        flag = None
        if contactLevel == appConst.contactHighStanding:
            flag = states.flagStandingHigh
        elif contactLevel == appConst.contactGoodStanding:
            flag = states.flagStandingGood
        elif contactLevel == appConst.contactNeutralStanding:
            flag = states.flagStandingNeutral
        elif contactLevel == appConst.contactBadStanding:
            flag = states.flagStandingBad
        elif contactLevel == appConst.contactHorribleStanding:
            flag = states.flagStandingHorrible
        if flag:
            flagContainer = AddAndSetFlagIcon(self, flag=flag, state=uiconst.UI_DISABLED, showHint=False)
            flagContainer.ChangeFlagPos(0, 0, 20, 20)
            Frame(parent=flagContainer, color=(1.0, 1.0, 1.0, 0.2))
            self.sr.selected = Frame(parent=flagContainer, color=(1.0, 1.0, 1.0, 0.75), state=uiconst.UI_DISABLED, idx=0)
            self.sr.selected.display = False
            self.sr.hilite = Frame(parent=flagContainer, color=(1.0, 1.0, 1.0, 0.75), state=uiconst.UI_DISABLED, idx=0)
            self.sr.hilite.display = False
            self.hint = text

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.sr.hilite:
            self.sr.hilite.display = True

    def OnMouseExit(self, *args):
        if self.sr.hilite:
            self.sr.hilite.display = False

    def OnSetFocus(self, *args):
        if self.sr.hilite:
            self.sr.hilite.display = True

    def OnKillFocus(self, *args):
        if self.sr.hilite:
            self.sr.hilite.display = False

    def OnChar(self, char, *args):
        if char in (uiconst.VK_SPACE, uiconst.VK_RETURN):
            self.parent.LevelOnClick(self.level, self)
