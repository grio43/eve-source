#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from characterdata.races import get_race_name
from eve.client.script.ui.const.eveIconConst import RACE_ICONS
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge
from eve.client.script.ui.login.charcreation_new import soundConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import COLOR_BY_FACTIONID, BLURB_BY_FACTIONID, MINIMIZE_ANIMATION_DURATION
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onEmpireFactionSelected, onEmpireFactionButtonClicked
from eve.common.lib import appConst
from eveui import Sprite
from localization import GetByLabel
ICONSIZE_SMALL = 70
ICONSIZE_LARGE = 100
OPACITY_IDLE = 0.7
OPACITY_HOVER = 1.0
BLURB_CONT_OFFSET = -180
BLURB_CONT_OFFSET_HOVER = -140

class EmpireSelectionButton(Container):
    default_name = 'EmpireIcon'
    default_state = uiconst.UI_NORMAL
    default_opacity = OPACITY_IDLE
    default_analyticID = ''

    def ApplyAttributes(self, attributes):
        super(EmpireSelectionButton, self).ApplyAttributes(attributes)
        self.factionID = attributes.factionID
        self.analyticID = attributes.get('analyticID', self.default_analyticID)
        self.isLarge = True
        raceID = appConst.raceByFaction[self.factionID]
        self.icon = Sprite(name='icon', parent=self, texturePath=RACE_ICONS[raceID], align=uiconst.CENTER, pos=(0,
         -10,
         ICONSIZE_LARGE,
         ICONSIZE_LARGE))
        self.nameLabel = EveCaptionLarge(name='NameLabel', parent=self, align=uiconst.CENTER, top=55, text=get_race_name(raceID))
        self.ConstructBlurbCont()

    def ConstructBlurbCont(self):
        self.blurbCont = Container(name='blurbCont', parent=self, align=uiconst.CENTERBOTTOM, pos=(0.0,
         BLURB_CONT_OFFSET,
         208,
         208), opacity=0.0)
        Sprite(name='topLine', parent=self.blurbCont, align=uiconst.CENTERBOTTOM, height=33, width=290, color=COLOR_BY_FACTIONID[self.factionID], texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/empireBottomGlow.png')
        EveLabelLarge(name='blurbLabel', parent=self.blurbCont, align=uiconst.CENTERBOTTOM, color=COLOR_BY_FACTIONID[self.factionID], top=30, width=198, text='<center>' + GetByLabel(BLURB_BY_FACTIONID[self.factionID]))

    def OnMouseEnter(self, *args):
        super(EmpireSelectionButton, self).OnMouseEnter(*args)
        PlaySound(soundConst.RACE_HOVER)
        animations.FadeTo(self, self.opacity, OPACITY_HOVER, duration=0.1)
        if self.isLarge:
            animations.FadeTo(self.blurbCont, self.blurbCont.opacity, 1.0, duration=0.6)
            animations.MorphScalar(self.blurbCont, 'top', self.blurbCont.top, BLURB_CONT_OFFSET_HOVER, duration=0.6)

    def OnMouseExit(self, *args):
        super(EmpireSelectionButton, self).OnMouseExit(*args)
        animations.FadeTo(self, self.opacity, OPACITY_IDLE, duration=0.1)
        if self.isLarge:
            self.FadeOutBlurbCont()

    def FadeOutBlurbCont(self, duration = 0.6):
        animations.FadeTo(self.blurbCont, self.blurbCont.opacity, 0.0, duration=duration)
        animations.MorphScalar(self.blurbCont, 'top', self.blurbCont.top, BLURB_CONT_OFFSET, duration=duration)

    def OnClick(self, *args):
        PlaySound(soundConst.RACE_SELECTION)
        log_button_clicked(self)
        onEmpireFactionButtonClicked(self.factionID)

    def ReduceSize(self):
        self.isLarge = False
        animations.FadeOut(self.nameLabel, duration=MINIMIZE_ANIMATION_DURATION)
        self.FadeOutBlurbCont(duration=MINIMIZE_ANIMATION_DURATION)
        animations.MorphScalar(self.icon, 'top', self.icon.top, 0, duration=MINIMIZE_ANIMATION_DURATION)
        animations.MorphScalar(self.icon, 'width', self.icon.width, ICONSIZE_SMALL, duration=MINIMIZE_ANIMATION_DURATION)
        animations.MorphScalar(self.icon, 'height', self.icon.height, ICONSIZE_SMALL, duration=MINIMIZE_ANIMATION_DURATION)
