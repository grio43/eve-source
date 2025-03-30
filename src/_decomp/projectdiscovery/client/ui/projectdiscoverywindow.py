#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\ui\projectdiscoverywindow.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from localization import GetByLabel
from math import pi
from projectdiscovery.client.ui.projectdiscoveryheader import ProjectDiscoveryWindowHeader
from projectdiscovery.client.util.dialogue import Dialogue

class BaseProjectDiscoveryWindow(Window):
    default_caption = GetByLabel('UI/ProjectDiscovery/ProjectName')
    default_windowID = 'ProjectDiscoveryWindow'
    default_isStackable = False
    default_isCollapseable = False
    default_iconNum = 'res:/UI/Texture/WindowIcons/projectdiscovery.png'
    default_minSize = (900, 600)
    default_showHelpInTutorial = False
    __notifyevents__ = ['OnProjectDiscoveryHeaderDragged',
     'OnProjectDiscoveryMouseDownOnHeader',
     'OnProjectDiscoveryTutorialFinished',
     'OnProjectDiscoveryClosed',
     'OnRestartWindow',
     'OnSolutionSubmit',
     'OnContinueFromRewards',
     'OnContinueToRewards',
     'OnShowProjectDiscoveryId',
     'OnUIColorsChanged',
     'OnUIScalingChange']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.show_help_in_tutorial = attributes.get('showHelpInTutorial', self.default_showHelpInTutorial)
        self.initialize()
        self.setup_layout()
        sm.RegisterNotify(self)

    def initialize(self):
        self._project_container = None
        self.player_statistics = None
        self.header_element = None
        self.help_button = None
        self.initialize_tutorial()
        self.initialize_statistics()

    def initialize_statistics(self):
        try:
            self.player_statistics = sm.RemoteSvc('ProjectDiscovery').get_player_statistics(get_history=True)
        except Exception:
            self.on_connection_error()

        self.player_exp_state = sm.RemoteSvc('ProjectDiscovery').get_player_state()

    def on_connection_error(self):
        self.show_connection_error_dialogue()

    def initialize_tutorial(self):
        self._is_tutorial_complete = sm.RemoteSvc('ProjectDiscovery').get_tutorial_completion_status()

    def on_help_button_clicked(self):
        self._setup_tutorial()

    def setup_layout(self):
        self.setup_side_panels()
        self.help_button = ButtonIcon(name='helpButton', parent=self.sr.main, align=uiconst.BOTTOMLEFT, iconSize=22, width=22, height=22, texturePath='res:/UI/Texture/WindowIcons/question.png', func=lambda : self.on_help_button_clicked())
        SetTooltipHeaderAndDescription(targetObject=self.help_button, headerText='', descriptionText=GetByLabel('UI/ProjectDiscovery/HelpTutorialTooltip'))
        self.project_container = Container(name='ProjectContainer', parent=self.sr.main, align=uiconst.TOALL, state=uiconst.UI_NORMAL, top=-20)
        self.set_background()
        self._bottom_container = Container(name='BottomContainer', parent=self.sr.main, align=uiconst.TOBOTTOM_NOPUSH, height=50, idx=0, padBottom=2)
        self.setup_tasks_id_components()
        self.header_element = ProjectDiscoveryWindowHeader(parent=self.sr.main.parent, align=uiconst.CENTERTOP, height=53, width=355, idx=0, top=2, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/headerBG.png', playerStatistics=self.player_statistics)
        if self.player_statistics:
            self._setup_project_type()
        self.set_background_fill()
        self.OnUIColorsChanged()

    def set_background(self):
        self._background_scene = None

    def set_background_fill(self):
        FillThemeColored(name='projectDiscovery_backgroundFill', align=uiconst.TOALL, parent=self.sr.main, padTop=-20, opacity=1)

    def setup_tasks_id_components(self):
        self._task_id_label_container = Container(name='TaskIdContainer', parent=self._bottom_container, align=uiconst.BOTTOMRIGHT, padBottom=10, padRight=10, width=100, height=20)
        self._task_id_label = Label(name='TaskId', parent=self._task_id_label_container, align=uiconst.CENTERRIGHT)

    def _setup_project_type(self):
        if self._is_tutorial_complete:
            self._setup_actual_project()
        else:
            self._setup_tutorial()

    def _setup_actual_project(self):
        self._clean()
        self.set_project()
        animations.FadeIn(self._project_container)
        self.update_help_button(is_visible=True)

    def set_project(self):
        raise NotImplementedError('set_project must be implemented in derived class for Project Discovery window')

    def _setup_tutorial(self):
        self._clean()
        self.set_tutorial()
        animations.FadeIn(self._project_container)
        self.update_help_button(is_visible=False)

    def set_tutorial(self):
        raise NotImplementedError('set_tutorial must be implemented in derived class for Project Discovery window')

    def _clean(self):
        if self._project_container:
            self._project_container.Close()
            self._bottom_container.Flush()
            self.setup_tasks_id_components()

    def setup_side_panels(self):
        SpriteThemeColored(name='RightPanel', parent=self.sr.main, align=uiconst.CENTERRIGHT, width=14, height=416, top=-20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')
        SpriteThemeColored(name='LeftPanel', parent=Transform(parent=self.sr.main, align=uiconst.CENTERLEFT, width=14, height=416, top=-20, rotation=pi), align=uiconst.TOLEFT_NOPUSH, width=14, height=416, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')

    def update_help_button(self, is_visible):
        state = uiconst.UI_NORMAL if is_visible or self.show_help_in_tutorial else uiconst.UI_HIDDEN
        self.help_button.SetState(state)

    def OnProjectDiscoveryTutorialFinished(self):
        self._project_container.Close()
        self._bottom_container.Flush()
        self._bottom_container.state = uiconst.UI_PICKCHILDREN
        self._setup_actual_project()

    def OnProjectDiscoveryHeaderDragged(self):
        if not self.IsLocked():
            self._BeginDrag()

    def OnProjectDiscoveryMouseDownOnHeader(self):
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)

    def OnProjectDiscoveryClosed(self):
        self.CloseByUser()

    def OnRestartWindow(self):
        self.CloseByUser()
        uicore.cmd.ToggleProjectDiscovery()

    def OnShowProjectDiscoveryId(self, id):
        self._task_id_label.SetText(id)
        animations.FadeIn(self._task_id_label)

    def OnContinueToRewards(self, *args, **kwargs):
        animations.FadeOut(self._task_id_label)

    def OnSolutionSubmit(self):
        if self.help_button:
            self.help_button.Disable(0)

    def OnContinueFromRewards(self, *args):
        if self.help_button:
            self.help_button.Enable()

    def OnStartMinimize_(self, *args):
        try:
            self._background_scene.Hide()
        except AttributeError:
            pass

    def OnStartMaximize_(self, *args):
        try:
            self._background_scene.Show()
        except AttributeError:
            pass

    def OnResizeUpdate(self, *args):
        self.resize()

    def OnUIScalingChange(self, *args):
        self.resize()

    def resize(self):
        scale = self.get_scale()
        if self._project_container:
            self._project_container.OnProjectDiscoveryRescaled(scale)
        sm.ScatterEvent('OnProjectDiscoveryRescaled', scale)

    def get_scale(self):
        scale = self.width / float(self.default_minSize[0])
        if self.width > self.height * (self.default_minSize[0] / float(self.default_minSize[1])):
            scale = self.height / float(self.default_minSize[1])
        return scale

    def show_connection_error_dialogue(self):
        self.dialogue = Dialogue(name='ConnectionErrorDialogue', parent=self.sr.main, align=uiconst.CENTER, width=450, height=150, messageText=GetByLabel('UI/ProjectDiscovery/ConnectionErrorDialogueMessage'), messageHeaderText=GetByLabel('UI/ProjectDiscovery/ConnectionErrorDialogueHeader'), label=GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=GetByLabel('UI/ProjectDiscovery/CloseProjectDiscoveryButtonLabel'), onCloseEvent='OnProjectDiscoveryClosed')

    def OnUIColorsChanged(self):
        if self.header_element is None:
            return
        color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIBASE)
        color = Color(*color).SetBrightness(1).GetRGBA()
        self.header_element.background_color = color
