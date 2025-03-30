#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihider\hider_mixin.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from logging import getLogger
from uihider.ui_hider_service import get_ui_hider_service
logger = getLogger(__name__)

class UiHiderMixin(object):

    def ApplyAttributes(self, attributes):
        super(UiHiderMixin, self).ApplyAttributes(attributes)
        if not self.GetUniqueName():
            logger.exception('Object has no unique name, unable to hide.')
            return
        self._update_hiding_state(only_hide=True)

    @property
    def is_hidden(self):
        if getattr(self, '_is_hidden', None) is None:
            self._is_hidden = self.IsHidden()
        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, is_hidden):
        self._is_hidden = is_hidden

    @property
    def ui_hider(self):
        if getattr(self, '_ui_hider', None) is None:
            self._ui_hider = get_ui_hider_service().get_ui_hider()
            self._ui_hider.subscribe(self._on_ui_hider_changed)
            ServiceManager.Instance().RegisterForNotifyEvent(ob=self, notify='OnUiHiderReset')
        return self._ui_hider

    @ui_hider.setter
    def ui_hider(self, ui_hider):
        if self._ui_hider:
            self._ui_hider.unsubscribe(self._on_ui_hider_changed)
        self._ui_hider = ui_hider
        self._ui_hider.subscribe(self._on_ui_hider_changed)

    def OnUiHiderReset(self, ui_hider):
        self.ui_hider = ui_hider

    def _on_ui_hider_changed(self):
        self._update_hiding_state()

    def _update_hiding_state(self, only_hide = False):
        is_hidden = self.ui_hider.is_ui_element_hidden(self.GetUniqueName())
        if self.is_hidden == is_hidden:
            return
        self.is_hidden = is_hidden
        if is_hidden:
            self._hide()
        elif not only_hide:
            self._show()

    def _hide(self):
        self.Hide()

    def _show(self):
        self.AnimateReveal()

    def ConstructAnimationReveal(self):
        x, y = self.GetAbsolutePosition()
        self.revealContainer = Container(name='revealContainer', parent=uicore.layer.main, align=uiconst.TOPLEFT, pos=(x,
         y,
         self.displayWidth,
         self.displayHeight), idx=0)
        self.revealFill = Fill(name='revealFill', parent=self.revealContainer, align=uiconst.CENTER, width=self.displayWidth, color=Color.GRAY, opacity=0.55)

    def AnimateReveal(self):
        if getattr(self, 'revealContainer', None) is not None:
            logger.warning('UiHider - Reveal container still exists, not animating the reveal.')
            return
        if self._IsMinimized():
            return
        self.opacity = 0
        self.Show()
        self.ConstructAnimationReveal()
        PlaySound('onboarding_ui_sfx_play')
        animations.MorphScalar(self.revealFill, 'height', startVal=0, endVal=self.displayHeight, duration=0.25)
        animations.BlinkIn(self.revealFill, startVal=0.2, endVal=self.revealFill.opacity, loops=3, timeOffset=0.25, callback=self.FadeInSelf)

    def CloseRevealContainer(self):
        self.revealContainer.Close()
        self.revealContainer = None

    def FadeInSelf(self):
        if self.revealFill:
            self.revealFill.Close()
        animations.FadeIn(self, duration=0.25, curveType=uiconst.ANIM_LINEAR, callback=self.CloseRevealContainer)

    def _IsMinimized(self):
        is_minimized_function = getattr(self, 'IsMinimized', None)
        if is_minimized_function and callable(is_minimized_function):
            return is_minimized_function()
        return False

    def _SetDisplay(self, value):
        if self.ui_hider.is_ui_element_hidden(self.GetUniqueName()):
            if not self._GetDisplay() and value:
                return
        super(UiHiderMixin, self)._SetDisplay(value)

    def SetState(self, state):
        if self.ui_hider.is_ui_element_hidden(self.GetUniqueName()):
            if self.GetState() == uiconst.UI_HIDDEN and state != uiconst.UI_HIDDEN:
                return
        super(UiHiderMixin, self).SetState(state)
