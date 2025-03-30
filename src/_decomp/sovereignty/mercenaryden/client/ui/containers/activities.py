#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\ui\containers\activities.py
from carbonui import Align, TextHeader, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from localization import GetByLabel
from sovereignty.mercenaryden.client.ui.containers.activity_cards import ActivityCards

class ActivitiesContainer(ContainerAutoSize):
    LABEL_PATH_TITLE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ActivitiesTitle'
    LABEL_PATH_TOOLTIP = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/ActivitiesTooltip'
    PADDING_TITLE_TO_TOOLTIP_ICON = 8
    PADDING_TITLE_TO_ACTIVITIES = 8
    ICON_SIZE_TOOLTIP = 16
    COLOR_TITLE_LABEL = TextColor.NORMAL

    def __init__(self, controller, *args, **kwargs):
        self._controller = controller
        super(ActivitiesContainer, self).__init__(*args, **kwargs)
        self._construct_content()

    def _construct_content(self):
        self._content = ContainerAutoSize(name='activities_content', parent=self, align=Align.TOTOP, display=False)
        self._construct_title()
        self._construct_activities()

    def _construct_title(self):
        title_container = Container(name='title_container', parent=self._content, align=Align.TOTOP)
        title_text = TextHeader(name='title_label', parent=title_container, align=Align.TOLEFT, color=self.COLOR_TITLE_LABEL, maxLines=1, text=GetByLabel(self.LABEL_PATH_TITLE))
        tooltip_icon_container = Container(name='tooltip_icon_container', parent=title_container, align=Align.TOLEFT, width=self.ICON_SIZE_TOOLTIP, padLeft=self.PADDING_TITLE_TO_TOOLTIP_ICON)
        InfoGlyphIcon(name='tooltip_icon', parent=tooltip_icon_container, align=Align.CENTER, width=self.ICON_SIZE_TOOLTIP, height=self.ICON_SIZE_TOOLTIP, hint=GetByLabel(self.LABEL_PATH_TOOLTIP))
        _, title_container.height = title_text.MeasureTextSize(title_text.text)

    def _construct_activities(self):
        ActivityCards(name='activities_container', parent=self._content, align=Align.TOTOP, padTop=self.PADDING_TITLE_TO_ACTIVITIES, controller=self._controller)

    def load_controller(self, controller):
        self._controller = controller
        should_show_mtos = self._controller.should_show_mtos()
        self._content.display = should_show_mtos
        self._content.SetSizeAutomatically()
        self.SetSizeAutomatically()

    def set_width(self, width):
        self.width = width
        self._content.SetSizeAutomatically()
        self.SetSizeAutomatically()
