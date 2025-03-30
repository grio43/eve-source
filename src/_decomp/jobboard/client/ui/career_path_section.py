#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\career_path_section.py
import carbonui
import eveui
import localization
from carbonui import Align
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.shared.careerPortal import careerConst
from jobboard.client import get_job_board_service
from metadata.common.content_tags.const import CONTENT_TAG_TO_CAREER_PATH

class CareerPathSection(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_clipChildren = True

    def __init__(self, *args, **kwargs):
        super(CareerPathSection, self).__init__(*args, **kwargs)
        self._layout()

    def _layout(self):
        top_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=28, padBottom=8)
        carbonui.TextHeader(parent=top_container, align=eveui.Align.center_left, maxLines=1, text=localization.GetByLabel('UI/Opportunities/BrowseByCareer'))
        cards_container = eveui.Container(parent=self, align=eveui.Align.to_top, height=120)
        left_cards = eveui.Container(parent=cards_container, align=eveui.Align.to_left_prop, width=0.5)
        CareerCard(parent=left_cards, align=eveui.Align.to_left_prop, width=0.5, controller=CareerCardController('enforcer'))
        CareerCard(parent=left_cards, align=eveui.Align.to_top, controller=CareerCardController('explorer'))
        right_cards = eveui.Container(parent=cards_container, align=eveui.Align.to_left_prop, width=0.5)
        CareerCard(parent=right_cards, align=eveui.Align.to_left_prop, width=0.5, controller=CareerCardController('industrialist'))
        CareerCard(parent=right_cards, align=eveui.Align.to_top, controller=CareerCardController('soldier_of_fortune'))


class CareerCard(eveui.Container):
    default_state = eveui.State.normal
    default_height = 120
    default_width = 100

    def __init__(self, controller, *args, **kwargs):
        super(CareerCard, self).__init__(*args, **kwargs)
        self._controller = controller
        self._layout()

    def _layout(self):
        self._hover_frame = eveui.Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=eveThemeColor.THEME_FOCUSDARK, opacity=0)
        content_container = eveui.ContainerAutoSize(name='content_container', parent=self, align=Align.VERTICALLY_CENTERED)
        icon_container = eveui.Container(name='icon_container', parent=content_container, align=Align.TOTOP, height=64)
        eveui.Sprite(parent=icon_container, align=eveui.Align.center, width=64, height=64, texturePath=self._controller.icon)
        carbonui.TextBody(parent=content_container, align=eveui.Align.to_top, text=self._controller.title, maxLines=2, textAlign=carbonui.TextAlign.CENTER, padBottom=8)

    def OnMouseEnter(self, *args):
        eveui.Sound.entry_hover.play()
        eveui.fade_in(self._hover_frame, end_value=0.3, duration=0.2)

    def OnMouseExit(self, *args):
        eveui.fade_out(self._hover_frame, duration=0.2)

    def OnClick(self, *args):
        eveui.Sound.button_click.play()
        get_job_board_service().open_browse_page(self._controller.content_tag_id)

    def OnColorThemeChanged(self):
        super(CareerCard, self).OnColorThemeChanged()
        self._hover_frame.rgb = eveThemeColor.THEME_FOCUSDARK[:3]


class CareerCardController(object):

    def __init__(self, career):
        self.career = career

    @property
    def content_tag_id(self):
        return 'career_path_{}'.format(self.career)

    @property
    def title(self):
        return careerConst.GetCareerPathName(self.career_id)

    @property
    def icon(self):
        return careerConst.ICON_BY_CAREER_ID[self.career_id]

    @property
    def career_id(self):
        return CONTENT_TAG_TO_CAREER_PATH[self.content_tag_id]
