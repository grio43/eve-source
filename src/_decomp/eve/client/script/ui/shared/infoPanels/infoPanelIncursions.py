#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelIncursions.py
import carbonui.const as uiconst
import blue
import trinity
import localization
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.shared.incursions.incursionConst import SCENETYPE_DATA
from eve.client.script.ui.shared.incursions.taleSystemEffect import TaleSystemEffect
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from localization import GetByLabel
from talecommon.const import scenesTypes, INCURSION_TEMPLATE_CLASSES
from carbonui.uicore import uicore
from talecommon.influence import CalculateDecayedInfluence
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
ICONSIZE = 22
ARROWS = ('ui_77_32_41', 'ui_77_32_42')
EFFECT_SPACING = 16
COLOR_ENABLED = (1, 1, 1, 0.75)
COLOR_DISABLED = (1, 1, 1, 0.25)
INCURSION_UPDATE_RATE = 60000

class InfoPanelIncursions(InfoPanelBase):
    default_name = 'InfoPanelIncursions'
    hasSettings = False
    panelTypeID = infoPanelConst.PANEL_INCURSIONS
    label = 'UI/Incursion/HUD/IncursionProfileTitle'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/taleDefaultIcon.png'
    default_severity = scenesTypes.vanguard
    default_height = 120
    __notifyevents__ = ['OnInfluenceUpdate', 'ProcessUpdateInfoPanel']

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.lastInfluence = None
        self.headerTextCont = Container(name='headerTextCont', parent=self.headerCont, align=uiconst.TOALL)
        self.title = self.headerCls(name='title', text='<color=white url=localsvc:method=ShowIncursionTab&constellationID=%d&open=1>%s</url>' % (session.constellationid, localization.GetByLabel(self.label)), parent=self.headerTextCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.subTitle = eveLabel.EveHeaderMedium(name='subtitle', parent=self.headerTextCont, left=self.title.width + 4, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, top=3)
        self.headerInfluenceBar = SystemInfluenceBar(parent=self.headerCont, state=uiconst.UI_HIDDEN, align=uiconst.TOALL, height=0, padding=(0, 6, 24, 6))
        self.headerInfluenceBar.OnClick = self.topCont.OnClick
        self.headerInfluenceBar.OnMouseEnter = self.topCont.OnMouseEnter
        self.headerInfluenceBar.OnMouseExit = self.topCont.OnMouseExit
        self.influenceBar = SystemInfluenceBar(parent=self.mainCont, padding=(0, 0, 0, 2))
        self.bottomContainer = Container(name='bottomContainer', parent=self.mainCont, align=uiconst.TOTOP, height=33)
        self.severityIcon = eveIcon.Icon(name='severityIcon', parent=self.bottomContainer, align=uiconst.CENTERLEFT, color=COLOR_ENABLED, pos=(0, 0, 32, 32), ignoreSize=True, size=48, state=uiconst.UI_NORMAL)
        self.iconCont = ContainerAutoSize(name='iconCont', parent=self.bottomContainer, align=uiconst.CENTERLEFT, pos=(40,
         0,
         0,
         ICONSIZE))
        self.finalEncounterIcon = IncursionFinalEncounterIcon(name='finalEncounterIcon', parent=self.bottomContainer, align=uiconst.CENTERRIGHT)
        self.effects = self._GetEffectsForTale()
        uthread.new(self.UpdateInfluenceThread)

    def _GetEffectsForTale(self):
        data = sm.GetService('incursion').GetActiveIncursionData()
        if not hasattr(data, 'effects'):
            return []
        return [ TaleSystemEffect(name=effectInfo['name'], align=uiconst.TOLEFT, parent=self.iconCont, color=COLOR_ENABLED, width=ICONSIZE, opacity=0.0, padRight=6, texturePath=effectInfo['texturePath'], hint=localization.GetByLabel(effectInfo['hint']), isScalable=effectInfo['isScalable']) for effectInfo in data.effects ]

    def ConstructCompact(self):
        data = sm.GetService('incursion').GetActiveIncursionData()
        self._SetFinalEncounterSpawned(data.hasFinalEncounter, data.templateClassID)
        influence = CalculateDecayedInfluence(data.influenceData)
        self.SetInfluence(influence, None, animate=False)

    def ConstructNormal(self):
        data = sm.GetService('incursion').GetActiveIncursionData()
        info = SCENETYPE_DATA[data.severity]
        influence = CalculateDecayedInfluence(data.influenceData)
        self.subTitle.text = localization.GetByLabel(info.subTitle)
        self.severityIcon.LoadIcon(info.severityIcon, ignoreSize=True)
        self.severityIcon.hint = localization.GetByLabel(info.hint)
        self._SetFinalEncounterSpawned(data.hasFinalEncounter, data.templateClassID)
        self.SetInfluence(influence, None, animate=False)
        self.severityIcon.opacity = 0.0

    def OnEndModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_NORMAL and oldMode:
            uicore.animations.BlinkIn(self.severityIcon)
            blue.synchro.SleepWallclock(200)
            for icon in self.effects:
                uicore.animations.BlinkIn(icon, endVal=COLOR_ENABLED[3])
                blue.synchro.SleepWallclock(50)

        else:
            self.severityIcon.opacity = 1.0
            for icon in self.effects:
                icon.opacity = COLOR_ENABLED[3]

    def OnStartModeChanged(self, oldMode):
        uthread.new(self._OnStartModeChanged, oldMode)

    def _OnStartModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_COMPACT:
            if oldMode:
                uicore.animations.FadeOut(self.headerTextCont, duration=0.3, sleep=True)
                self.headerTextCont.Hide()
                self.headerInfluenceBar.Show()
                uicore.animations.FadeTo(self.headerInfluenceBar, 0.0, 1.0, duration=0.3)
            else:
                self.headerTextCont.Hide()
                self.headerInfluenceBar.Show()
        elif self.headerInfluenceBar.display:
            uicore.animations.FadeOut(self.headerInfluenceBar, duration=0.3, sleep=True)
            self.headerInfluenceBar.Hide()
            self.headerTextCont.Show()
            uicore.animations.FadeTo(self.headerTextCont, 0.0, 1.0, duration=0.3)

    @staticmethod
    def IsAvailable():
        return sm.GetService('incursion').IsIncursionActive()

    def UpdateInfluenceThread(self):
        while not self.destroyed:
            newInfluence = None
            data = sm.GetService('incursion').GetActiveIncursionData()
            if data:
                newInfluence = CalculateDecayedInfluence(data.influenceData)
                if self.lastInfluence is None or self.lastInfluence != newInfluence:
                    self.SetInfluence(newInfluence, False, True)
            blue.pyos.synchro.SleepWallclock(INCURSION_UPDATE_RATE)

    def SetInfluence(self, influence, positiveProgress, animate = True):
        self.influenceBar.SetInfluence(influence, positiveProgress, animate)
        self.headerInfluenceBar.SetInfluence(influence, positiveProgress, animate)
        for icon in self.effects:
            icon.SetInfluence(influence)

        self.lastInfluence = influence

    def OnInfluenceUpdate(self, taleID, newInfluenceData):
        data = sm.GetService('incursion').GetActiveIncursionData()
        if data and data.taleID == taleID:
            influenceData = data.influenceData
            oldInfluence = CalculateDecayedInfluence(influenceData)
            influenceData.influence = newInfluenceData.influence
            influenceData.lastUpdated = newInfluenceData.lastUpdated
            newInfluence = CalculateDecayedInfluence(influenceData)
            positiveProgress = oldInfluence < newInfluence
            self.SetInfluence(newInfluence, positiveProgress)

    def _SetFinalEncounterSpawned(self, hasSpawned, templateClassId):
        if templateClassId in INCURSION_TEMPLATE_CLASSES:
            self.finalEncounterIcon.SetFinalEncounterSpawned(hasSpawned)


class IncursionFinalEncounterIcon(Sprite):
    default_name = 'finalEncounterIcon'
    default_texturePath = 'res:/UI/Texture/classes/Incursions/iconMothership.png'
    default_state = uiconst.UI_NORMAL
    default_width = 32
    default_height = 32

    def ApplyAttributes(self, attributes):
        super(IncursionFinalEncounterIcon, self).ApplyAttributes(attributes)
        hasSpawned = attributes.get('hasSpawned', False)
        self.SetFinalEncounterSpawned(hasSpawned)

    def SetFinalEncounterSpawned(self, hasSpawned):
        self.hasSpawned = hasSpawned
        self.SetRGBA(*(COLOR_ENABLED if hasSpawned else COLOR_DISABLED))

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        text = self._GetTooltipText()
        tooltipPanel.AddLabelMedium(text=text, wrapWidth=250)

    def _GetTooltipText(self):
        if self.hasSpawned:
            return GetByLabel('UI/Incursion/HUD/IncursionFinalEncounterReportHint')
        else:
            return GetByLabel('UI/Incursion/HUD/NoIncursionFinalEncounterHint')


class BarFill(Sprite):
    __guid__ = 'uicls.BarFill'
    default_name = 'BarFill'
    default_rect = (0, 0, 0, 32)
    default_texturePath = 'res:/ui/texture/classes/InfluenceBar/influenceBarDefault.png'
    default_slice = None
    default_state = uiconst.UI_HIDDEN
    default_align = uiconst.RELATIVE
    default_spriteEffect = trinity.TR2_SFX_COPY
    TEX_SIZE = 134

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        slice = attributes.get('slice', self.default_slice)
        if slice is not None:
            self.SetTextureSlice(slice)

    def SetTextureSlice(self, slice):
        self.SetTexturePath(slice)

    def SetBar(self, delta):
        if not self.parent:
            return
        ppl, ppt, mainBarWidth, h = self.parent.parent.GetAbsolute()
        pl, pt, parentWidth, h = self.parent.GetAbsolute()
        barOffset = pl - ppl
        self.left = int(-barOffset + mainBarWidth - round(mainBarWidth * delta))
        self.width = mainBarWidth


class SystemInfluenceBar(Container):
    __guid__ = 'uicls.SystemInfluenceBar'
    default_name = 'SystemInfluenceBar'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 12
    default_influence = 0.0
    default_align = uiconst.TOTOP
    default_padTop = 4
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    FRAME_COLOR = (0.5, 0.5, 0.5, 1.0)
    TEX_WIDTH = 256
    PADDING = (0, 4, 0, 4)
    ARROW_HEIGHT = 32
    LEFT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarNegative.png'
    RIGHT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarPositive.png'
    HINT_LABEL = 'UI/Incursion/HUD/InfluenceBarHint'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        l, t, w, h = self.GetAbsolute()
        self.influence = attributes.get('influence', 0.0)
        self.targetInfluence = self.influence
        self.blueBar = Container(parent=self, name='blueBar', align=uiconst.TOLEFT_PROP, width=0, clipChildren=True)
        Fill(name='blueBase', parent=self.blueBar, color=(0, 1, 1, 0.25))
        self.blueArrows = BarFill(name='blueFill', pos=(0,
         0,
         w,
         h), parent=self.blueBar, color=(0, 1, 1, 0.75))
        self.knob = Line(parent=self, name='sliderKnob', color=self.FRAME_COLOR, align=uiconst.TOLEFT)
        self.redBar = Container(parent=self, name='redBar', align=uiconst.TOALL, clipChildren=True)
        Fill(name='redBase', parent=self.redBar, color=(1, 0, 0, 0.25))
        self.redArrows = BarFill(pos=(0,
         0,
         w,
         h), name='redFill', parent=self.redBar, color=(1, 0, 0, 0.75))

    def SetInfluence(self, influence, positiveProgress, animate = True):
        if self.HINT_LABEL is not None:
            self.SetHint(localization.GetByLabel(self.HINT_LABEL, influence=int(round((1.0 - influence) * 100))))
        if animate:
            self.targetInfluence = influence
            self.animationTimer = AutoTimer(100, self.Animation_Thread, positiveProgress)
        else:
            self.influence = self.targetInfluence = influence
            self.blueBar.width = influence

    def Animation_Thread(self, positiveProgress):
        l, t, w, h = self.GetAbsolute()
        totalWidth = w - self.knob.width
        count = 5
        if positiveProgress is None:
            moveFunc = None
            self.blueArrows.state = uiconst.UI_HIDDEN
            self.redArrows.state = uiconst.UI_HIDDEN
        elif positiveProgress:
            moveFunc = self.MoveRight
            self.blueArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        else:
            moveFunc = self.MoveLeft
            self.blueArrows.SetTextureSlice(self.LEFT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.LEFT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        while count > 0:
            start = blue.os.GetWallclockTime()
            lastDelta = delta = 0.0
            while delta < 2.0:
                delta = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 1000.0, 2.0))
                dt = delta - lastDelta
                if self.targetInfluence > self.influence:
                    self.influence = min(self.influence + 0.25 * dt, self.targetInfluence)
                else:
                    self.influence = max(self.influence - 0.25 * dt, self.targetInfluence)
                self.blueBar.width = self.influence
                if moveFunc:
                    moveFunc(delta)
                lastDelta = delta
                blue.pyos.synchro.Yield()
                if not self or self.destroyed:
                    return

            count -= 1

        self.animationTimer = None

    def MoveRight(self, delta):
        self.blueArrows.SetBar(2.0 - delta)
        self.redArrows.SetBar(2.0 - delta)

    def MoveLeft(self, delta):
        self.blueArrows.SetBar(delta)
        self.redArrows.SetBar(delta)
