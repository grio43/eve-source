#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\componentInfo.py
from carbonui import Align, TextBody, TextColor, TextHeadline
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.cosmetics.ship.controls.numRunsIndicator import NumRunsIndicator
from eve.client.script.ui.cosmetics.ship.controls.rarityIndicator import RarityIndicator
from localization import GetByLabel

class ComponentInfo(FlowContainer):

    def __init__(self, component_data, license_type, runs_remaining, contentSpacing = (8, 8), *args, **kwargs):
        super(ComponentInfo, self).__init__(contentSpacing=contentSpacing, *args, **kwargs)
        self.component_data = component_data
        self.license_type = license_type
        self.runs_remaining = runs_remaining
        self.construct_layout()

    def construct_layout(self):
        self.name_and_icon_cont = ContainerAutoSize(parent=self, height=56)
        self.construct_rarity_icon()
        self.construct_label()
        self.construct_runs()

    def construct_rarity_icon(self):
        icon_container = Container(name='icon_container', parent=self.name_and_icon_cont, align=Align.TOLEFT, pos=(0, 0, 56, 56), bgColor=(1, 1, 1, 0.1))
        RarityIndicator(name='rarity_indicator', parent=icon_container, align=Align.CENTER, rarity=self.component_data.rarity)

    def construct_label(self):
        name_container = ContainerAutoSize(name='name_container', parent=self.name_and_icon_cont, align=Align.TOLEFT, bgColor=eveThemeColor.THEME_TINT)
        TextHeadline(name='name_label', parent=name_container, align=Align.CENTER, text=self.component_data.name, padding=(16, 0, 16, 0))

    def construct_runs(self):
        runs_container = ContainerAutoSize(name='runs_container', parent=self, minHeight=52)
        NumRunsIndicator(parent=runs_container, licence_type=self.license_type, num_runs=self.runs_remaining, align=Align.CENTERLEFT, pos=(0, 0, 32, 32))
        TextBody(name='runs_label', parent=runs_container, align=Align.CENTERLEFT, left=40, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Sequencing/SequencingRuns'), color=TextColor.SECONDARY)
