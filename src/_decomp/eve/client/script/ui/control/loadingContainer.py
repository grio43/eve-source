#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\loadingContainer.py
import uthread2
import trinity
import eveicon
import logging
from carbonui import ButtonVariant, Density, TextAlign, uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.childrenlist import PyChildrenList
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelLarge
from eve.client.script.ui import eveColor
from itertoolsext.Enum import Enum
from sovereignty.mercenaryden.common.errors import ServiceUnavailable
logger = logging.getLogger(__name__)

@Enum

class LoadingSpriteSize(object):
    SMALL = 16
    MEDIUM = 32
    LARGE = 64


@Enum

class LoadingContainerState(object):
    LOADING = 'loading'
    LOADED = 'loaded'
    FAILED = 'failure'


class LoadingContainer(Container):
    _loadingSpriteFadeDuration = 0.1
    _contentsFadeDuration = 0.2
    _failureStateFadeDuration = 0.2
    loadingSpriteFadeDelay = 0.0
    failureContPadding = 16

    def __init__(self, loadCallback = None, failedCallback = None, loadingSpriteSize = LoadingSpriteSize.MEDIUM, failureStateMessage = '', failureStateSubtext = '', retryBtnLabel = '', **kw):
        self._state = None
        self._loadingThread = None
        self._contentsCont = None
        self._failureStateCont = None
        self._loadCallback = loadCallback
        self._failedCallback = failedCallback
        self._loadingSpriteSize = loadingSpriteSize
        super(LoadingContainer, self).__init__(**kw)
        self._ConstructLayout(failureStateMessage, failureStateSubtext, retryBtnLabel)
        self.children = LoadingGroupChildrenList(self)

    def Close(self):
        if self._loadingThread:
            self._loadingThread.kill()
            self._loadingThread = None
        super(LoadingContainer, self).Close()

    @property
    def contents(self):
        return self._contentsCont

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value != self._state:
            self._state = value
            if self._state == LoadingContainerState.LOADING:
                self._HideFailureCont()
                self._HideContents()
                self._ShowLoadingSprite()
            elif self._state == LoadingContainerState.LOADED:
                self._HideFailureCont()
                self._HideLoadingSprite()
                self._ShowContents()
            elif self._state == LoadingContainerState.FAILED:
                self._HideLoadingSprite()
                self._HideContents()
                self._ShowFailureCont()

    def _ConstructLayout(self, failureStateMessage, failureStateSubtext, retryBtnLabel):
        self._failureStateCont = Container(parent=self, name='failureStateCont', opacity=0.0)
        self._contentsCont = Container(parent=self, name='contentsCont', opacity=0.0)
        self._ConstructFailureState(failureStateMessage, failureStateSubtext, retryBtnLabel)
        self._ConstructLoadingSprite()

    def _ConstructFailureState(self, failureStateMessage, failureStateSubtext, retryBtnLabel):
        self._failureCentralCont = ContainerAutoSize(name='failureCentralCont', parent=self._failureStateCont, align=uiconst.CENTER, padding=(self.failureContPadding,
         self.failureContPadding,
         self.failureContPadding,
         self.failureContPadding))
        if len(failureStateMessage) > 0:
            errorMessage = EveCaptionSmall(name='errorMessage', parent=self._failureCentralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text=failureStateMessage, color=eveColor.WARNING_ORANGE)
            errorMessage.uppercase = True
        if len(failureStateSubtext) > 0:
            EveLabelLarge(name='errorSubtext', parent=self._failureCentralCont, align=uiconst.TOTOP, textAlign=TextAlign.CENTER, text=failureStateSubtext, top=8 if len(failureStateMessage) > 0 else 0)
        if len(retryBtnLabel) > 0:
            btnCont = ContainerAutoSize(name='btnCont', parent=self._failureCentralCont, align=uiconst.TOTOP, height=32, top=16 if len(failureStateMessage) + len(failureStateSubtext) > 0 else 0)
            Button(name='retryBtn', parent=btnCont, align=uiconst.CENTER, density=Density.NORMAL, label=retryBtnLabel, texturePath=eveicon.refresh, variant=ButtonVariant.GHOST, func=lambda *args: self.LoadContent(self._loadCallback, self._failedCallback))

    def _ConstructLoadingSprite(self):
        self._loadingSprite = StreamingVideoSprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self._loadingSpriteSize, height=self._loadingSpriteSize, videoPath='res:/video/shared/loading_sprite_%s.webm' % self._loadingSpriteSize, videoLoop=True, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, opacity=0.0)

    def LoadContent(self, loadCallback = None, failedCallback = None):
        self._loadCallback = loadCallback
        self._failedCallback = failedCallback
        if self._loadingThread is None:
            self._loadingThread = uthread2.StartTasklet(self._LoadContentThread)

    def _LoadContentThread(self):
        try:
            self.state = LoadingContainerState.LOADING
            self._loadCallback()
            self.state = LoadingContainerState.LOADED
        except ServiceUnavailable as e:
            self.state = LoadingContainerState.FAILED
            logger.warning('LoadingContainer: timeout in _LoadContentThread: %s', e)
        except Exception as e:
            self.state = LoadingContainerState.FAILED
            logger.exception('LoadingContainer: exception in _LoadContentThread: %s', e)
            if self._failedCallback:
                self._failedCallback(e)
            else:
                raise
        finally:
            self._loadingThread = None

    def _HideContents(self):
        animations.FadeTo(self._contentsCont, self._contentsCont.opacity, 0.0, duration=self._contentsFadeDuration)

    def _ShowContents(self):
        animations.FadeTo(self._contentsCont, self._contentsCont.opacity, 1.0, duration=self._contentsFadeDuration)

    def _HideLoadingSprite(self):
        animations.FadeTo(self._loadingSprite, self._loadingSprite.opacity, 0.0, duration=self._loadingSpriteFadeDuration)

    def _ShowLoadingSprite(self):
        animations.FadeTo(self._loadingSprite, self._loadingSprite.opacity, 1.0, duration=self._loadingSpriteFadeDuration, timeOffset=self.loadingSpriteFadeDelay)

    def _ShowFailureCont(self):
        self._failureStateCont.Enable()
        animations.FadeTo(self._failureStateCont, self._failureStateCont.opacity, 1.0, duration=self._failureStateFadeDuration)

    def _HideFailureCont(self):
        animations.FadeTo(self._failureStateCont, self._failureStateCont.opacity, 0.0, duration=self._failureStateFadeDuration)
        self._failureStateCont.Disable()

    def Flush(self):
        self._contentsCont.Flush()

    def _OnSizeChange_NoBlock(self, width, height):
        super(LoadingContainer, self)._OnSizeChange_NoBlock(width, height)
        if hasattr(self, '_failureCentralCont'):
            self._failureCentralCont.width = width


class LoadingGroupChildrenList(PyChildrenList):

    def __init__(self, parentCont):
        super(LoadingGroupChildrenList, self).__init__(owner=parentCont, children=parentCont.children)

    def append(self, obj):
        return self.insert(-1, obj)

    def insert(self, idx, obj):
        parentCont = self.GetOwner()
        if parentCont:
            parentCont.contents.children.insert(idx, obj)
            return self
