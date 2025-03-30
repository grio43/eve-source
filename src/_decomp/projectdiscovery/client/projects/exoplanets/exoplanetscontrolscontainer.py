#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\exoplanetscontrolscontainer.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.control.button import Button
from carbonui.util.color import Color
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from projectdiscovery.client.projects.exoplanets.detrendingcontrolpanel import DetrendingControlPanel
from carbonui.uianimations import animations
from carbonui.uicore import uicore
import trinity
import math
import localization

class ExoPlanetsControlsContainer(Container):
    __notifyevents__ = ['OnTransitMarkingWithPeriod',
     'OnTransitMarkingCancelledAfterSettingPeriod',
     'OnCalibrateToFolded',
     'OnCalibrateToUnFolded',
     'OnFoldButtonPressed',
     'OnDiscardButtonPressed',
     'OnConfirmButtonPressed',
     'OnExoPlanetsControlsInitialize',
     'OnShowProjectDiscoveryResultBackButton',
     'OnProjectDiscoveryResultBackButtonPressed']

    def ApplyAttributes(self, attributes):
        super(ExoPlanetsControlsContainer, self).ApplyAttributes(attributes)
        self.setup_layout()
        sm.RegisterNotify(self)

    def setup_layout(self):
        self._setup_confirmation_container()
        self._setup_fold_button_container()
        self._setup_result_back_button()
        self._detrend_control_panel = DetrendingControlPanel(name='DetrendingControlPanel', parent=self, align=uiconst.CENTERLEFT)

    def _setup_fold_button_container(self):
        self._fold_button_container = ContainerAutoSize(name='FoldButtonContainer', parent=self, align=uiconst.CENTER, height=20, state=uiconst.UI_HIDDEN)
        self._left_fold_arrow_container = Container(name='LeftArrowContainer', parent=self._fold_button_container, align=uiconst.TOLEFT, width=100)
        self._left_fold_arrow = Sprite(bgParent=self._left_fold_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self._fold_button = Button(name='ExoPlanetsFoldButton', parent=self._fold_button_container, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/FoldButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=25, func=lambda args: sm.ScatterEvent('OnFoldButtonPressed'))
        SetTooltipHeaderAndDescription(targetObject=self._fold_button, headerText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/FoldingTooltipHeader'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/FoldingTooltipMessage'))
        self._right_fold_arrow_container = Container(name='RightArrowContainer', parent=Transform(parent=self._fold_button_container, width=100, align=uiconst.TOLEFT, rotation=math.pi), align=uiconst.TOLEFT, width=100)
        self._right_fold_arrow = Sprite(bgParent=self._right_fold_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self.animate_arrows(self._left_fold_arrow)
        self.animate_arrows(self._right_fold_arrow)

    def _setup_confirmation_container(self):
        self._confirmation_container = ContainerAutoSize(name='ConfirmationContainer', parent=self, align=uiconst.CENTER, height=20, state=uiconst.UI_HIDDEN)
        self._left_arrow_container = Container(name='LeftArrowContainer', parent=self._confirmation_container, align=uiconst.TOLEFT, width=100)
        self._left_confirmation_arrow = Sprite(bgParent=self._left_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self._confirm_button = Button(name='ExoPlanetsConfirmButton', parent=self._confirmation_container, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ConfirmButtonLabel'), fontsize=16, fixedheight=20, padRight=5, func=lambda args: sm.ScatterEvent('OnConfirmButtonPressed'))
        SetTooltipHeaderAndDescription(targetObject=self._confirm_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ConfirmButtonTooltip'))
        self._discard_button = Button(name='ExoPlanetsDiscardButton', parent=self._confirmation_container, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/DiscardButtonLabel'), fontsize=16, fixedheight=20, padLeft=5, func=lambda args: sm.ScatterEvent('OnDiscardButtonPressed'))
        SetTooltipHeaderAndDescription(targetObject=self._discard_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/DiscardButtonToolTip'))
        self._right_arrow_container = Container(name='RightArrowContainer', parent=Transform(parent=self._confirmation_container, width=100, align=uiconst.TOLEFT, rotation=math.pi), align=uiconst.TOLEFT, width=100)
        self._right_confirmation_arrow = Sprite(bgParent=self._right_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self.animate_arrows(self._left_confirmation_arrow)
        self.animate_arrows(self._right_confirmation_arrow)

    def _setup_result_back_button(self):
        self._back_container = ContainerAutoSize(name='ConfirmationContainer', parent=self, align=uiconst.CENTER, height=20, state=uiconst.UI_HIDDEN)
        left_arrow_container = Container(name='LeftArrowContainer', parent=self._back_container, align=uiconst.TOLEFT, width=100)
        left_arrow = Sprite(bgParent=left_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self._back_button = Button(name='ExoPlanetsConfirmButton', parent=self._back_container, align=uiconst.TOLEFT, label=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/BackButtonLabel'), fontsize=16, fixedheight=20, padRight=5, func=lambda args: sm.ScatterEvent('OnProjectDiscoveryResultBackButtonPressed'))
        right_arrow_container = Container(name='RightArrowContainer', parent=Transform(parent=self._back_container, width=100, align=uiconst.TOLEFT, rotation=math.pi), align=uiconst.TOLEFT, width=100)
        right_arrow = Sprite(bgParent=right_arrow_container, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self.animate_arrows(left_arrow)
        self.animate_arrows(right_arrow)

    def OnExoPlanetsControlsInitialize(self):
        self.initialize()

    def OnTransitMarkingWithPeriod(self):
        self._fold_button_container.SetState(uiconst.UI_NORMAL)
        animations.BlinkIn(self._fold_button)

    def OnTransitMarkingCancelledAfterSettingPeriod(self):
        self.initialize()

    def OnDiscardButtonPressed(self):
        self._confirmation_container.SetState(uiconst.UI_HIDDEN)
        self._detrend_control_panel.Disable()

    def OnConfirmButtonPressed(self):
        self._confirmation_container.SetState(uiconst.UI_HIDDEN)
        self._detrend_control_panel.Disable()

    def initialize(self):
        self._fold_button_container.SetState(uiconst.UI_HIDDEN)
        self._confirmation_container.SetState(uiconst.UI_HIDDEN)
        self._back_container.SetState(uiconst.UI_HIDDEN)

    def OnFoldButtonPressed(self):
        self._fold_button_container.SetState(uiconst.UI_HIDDEN)
        self._detrend_control_panel.Disable()

    def OnCalibrateToFolded(self):
        self._confirmation_container.SetState(uiconst.UI_NORMAL)
        animations.BlinkIn(self._confirmation_container)
        self._detrend_control_panel.Enable()

    def OnCalibrateToUnFolded(self):
        self._detrend_control_panel.Enable()

    def OnShowProjectDiscoveryResultBackButton(self):
        self._back_container.SetState(uiconst.UI_PICKCHILDREN)

    def OnProjectDiscoveryResultBackButtonPressed(self):
        self.initialize()

    def animate_arrows(self, arrows):
        if self.destroyed:
            return
        arrows.Show()
        if arrows.isAnimated:
            return
        diff = math.fabs(-0.16 - arrows.translationSecondary[0])
        duration = diff / 0.16
        if diff > 0.001:
            uicore.animations.MorphVector2(arrows, 'translationSecondary', arrows.translationSecondary, (-0.16, 0.0), duration=duration, curveType=uiconst.ANIM_LINEAR, callback=lambda : self._loop_arrow_animation(arrows))
        else:
            self._loop_arrow_animation(arrows)

    def _loop_arrow_animation(self, arrows):
        uicore.animations.MorphVector2(arrows, 'translationSecondary', (0.16, 0.0), (-0.16, 0.0), duration=2.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    @property
    def detrending_panel(self):
        return self._detrend_control_panel

    @property
    def folding_controls(self):
        return self._fold_button_container

    @property
    def confirm_button_container(self):
        return self._confirmation_container
