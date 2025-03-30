#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\reward_info_container.py
import eveui
import carbonui
from carbonui import Align, TextColor, uiconst

class RewardInfoContainer(eveui.ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_alignMode = Align.TOTOP
    default_minHeight = 32
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(RewardInfoContainer, self).ApplyAttributes(attributes)
        caption = attributes.caption
        icon = attributes.icon
        text = attributes.text
        tooltip = attributes.tooltip
        job = attributes.job
        if icon:
            if job:
                icon_container = DetailIconContainer(name='icon_container', parent=self, align=Align.CENTERLEFT, width=32, height=32, bgTexturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', bgColor=(1, 1, 1, 0.05), job=job, tooltipsCls=tooltip)
            else:
                icon_container = eveui.Container(name='icon_container', parent=self, align=Align.CENTERLEFT, width=32, height=32, bgTexturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', bgColor=(1, 1, 1, 0.05))
            self._icon = eveui.Sprite(name='icon', parent=icon_container, align=Align.CENTER, color=TextColor.SECONDARY, width=16, height=16, texturePath=icon)
        if text:
            self._text = carbonui.TextBody(parent=self, align=Align.TOTOP, text=text, maxLines=1, autoFadeSides=16, pickState=carbonui.PickState.ON, padLeft=38)
            self._caption = carbonui.TextDetail(parent=self, align=Align.TOTOP, text=caption, maxLines=1, autoFadeSides=16, color=TextColor.SECONDARY, padLeft=38)

    @property
    def text(self):
        return self._text.text

    @text.setter
    def text(self, txt):
        self._text.text = txt

    @property
    def caption(self):
        return self._caption.text

    @caption.setter
    def caption(self, value):
        self._caption.text = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon.texturePath = value


class DetailIconContainer(eveui.Container):
    default_state = eveui.State.normal

    def __init__(self, job, tooltipsCls = None, *args, **kwargs):
        self._job = job
        self._tooltipCls = tooltipsCls
        super(DetailIconContainer, self).__init__(*args, **kwargs)

    def ConstructTooltipPanel(self):
        return self._tooltipCls(job=self._job)
