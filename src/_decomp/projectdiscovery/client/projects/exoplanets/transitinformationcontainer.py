#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\transitinformationcontainer.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium
from carbonui.uianimations import animations
import carbonui.const as uiconst
import localization
from projectdiscovery.client.projects.exoplanets.exoplanetsutil import result
from projectdiscovery.client import const

class TransitInformationContainer(Container):
    __notifyevents__ = ['OnDisplayTransitInformation', 'OnHideTransitInformation']
    default_state = uiconst.UI_HIDDEN
    default_opacity = 0

    def ApplyAttributes(self, attributes):
        super(TransitInformationContainer, self).ApplyAttributes(attributes)
        self._title = None
        self._object_label = None
        self._transit_info_label = None
        self._setup_layout()
        sm.RegisterNotify(self)

    def _setup_layout(self):
        _title_container = Container(name='TitleContainer', parent=self, align=uiconst.TOTOP, height=20)
        self._title_text_container = ContainerAutoSize(name='TitleTextContainer', parent=_title_container, align=uiconst.TORIGHT)
        self._sprite_container = Container(name='SpriteContainer', parent=_title_container, align=uiconst.TORIGHT, width=16, padRight=10)
        self._state_sprite = Sprite(name='StateSprite', parent=self._sprite_container, align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/classes/ProjectDiscovery/result_fail.png', color=const.Colors.RED)

    def _show_title(self, title_text, color):
        if self._title:
            self._title.Close()
        self._title = EveCaptionSmall(name='Title', parent=self._title_text_container, align=uiconst.CENTERLEFT, text=title_text, color=color, autoFitToText=True, idx=0)

    def _show_object_label(self, object_label_text):
        if self._object_label:
            self._object_label.Close()
        self._object_label = EveLabelMedium(name='ObjectLabel', parent=self, align=uiconst.TOPRIGHT, top=25, text=object_label_text, autoFitToText=True)

    def _show_transit_info_label(self, transit_info_text):
        if self._transit_info_label:
            self._transit_info_label.Close()
        self._transit_info_label = EveLabelMedium(name='TransitInfoLabel', parent=self, align=uiconst.TOPRIGHT, top=45, text=transit_info_text, autoFitToText=True)

    def OnDisplayTransitInformation(self, transit_marker, state = None, epoch = None):
        self._load_information(transit_marker, state=state, epoch=epoch)
        self.state = uiconst.UI_PICKCHILDREN
        animations.BlinkIn(self)

    def OnHideTransitInformation(self):
        animations.BlinkOut(self, callback=lambda : self.SetState(uiconst.UI_HIDDEN))

    def _load_information(self, transit_marker, state = None, epoch = None):
        if transit_marker:
            orbital_period = round(transit_marker.get_period_length(), 3) if transit_marker.get_period_length() else localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NotApplicable')
            orbital_text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/PeriodInfo', period=orbital_period)
            epoch_text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/EpochInfo', epoch=round(transit_marker.get_epoch(), 3))
            object_text = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ObjectInfo', objecttype=transit_marker.get_transit_type())
            self._show_object_label(object_text)
            self._show_transit_info_label(epoch_text + ' - ' + orbital_text)
        else:
            epoch = epoch if epoch else localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NotApplicable')
            self._show_object_label(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/ObjectInfo', objecttype=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NotApplicable')))
            self._show_transit_info_label(localization.GetByLabel('UI/ProjectDiscovery/exoplanets/EpochInfo', epoch=epoch) + ' - ' + localization.GetByLabel('UI/ProjectDiscovery/exoplanets/PeriodListing', period=localization.GetByLabel('UI/ProjectDiscovery/exoplanets/NotApplicable')))
        color = const.Colors.RED
        texture_path = 'res:/UI/Texture/classes/ProjectDiscovery/result_fail.png'
        title = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/InaccurateMarking')
        if state == result.ResultStates.CORRECT:
            color = const.Colors.GREEN
            texture_path = 'res:/UI/Texture/classes/ProjectDiscovery/result_success.png'
            title = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/AccurateMarking')
        elif state == result.ResultStates.MISSED:
            color = const.Colors.YELLOW
            texture_path = 'res:/UI/Texture/classes/ProjectDiscovery/result_missed.png'
            title = localization.GetByLabel('UI/ProjectDiscovery/exoplanets/MissedMarking')
        self._state_sprite.color = color
        self._state_sprite.SetTexturePath(texture_path)
        self._state_sprite.ReloadTexture()
        self._show_title(title, color)
