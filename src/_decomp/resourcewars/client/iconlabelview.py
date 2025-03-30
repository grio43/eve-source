#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\iconlabelview.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
import carbonui.const as uiconst
from carbonui.fontconst import STYLE_DEFAULT
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.util.uix import GetTextWidth
from inventorycommon.const import typeCorporation
from localization import GetByLabel
import log
from uthread2 import StartTasklet

class IconLabelView(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.text = attributes.text
        self.icon_texture = attributes.icon_texture
        self.font_size = attributes.font_size
        self.icon_size = attributes.icon_size
        row_height = attributes.row_height
        row_margin_icon = attributes.row_margin_icon
        row_margin_internal = attributes.Get('row_margin_internal', 0)
        scale = attributes.Get('scale', 1.0)
        scaled_font_size = self._get_font_size(scale)
        scaled_icon_size = self._get_icon_size(scale)
        text_width = GetTextWidth(self.text, fontsize=scaled_font_size, fontStyle=STYLE_DEFAULT)
        attributes.width = scaled_icon_size + row_margin_icon + text_width
        attributes.left = row_margin_internal
        super(IconLabelView, self).ApplyAttributes(attributes)
        self.icon = Sprite(name='rewardView_icon', parent=self, align=uiconst.CENTERLEFT, texturePath=self.icon_texture, width=scaled_icon_size, height=scaled_icon_size, state=uiconst.UI_PICKCHILDREN)
        self.label_container = Container(name='rewardView_labelContainer', parent=self, align=uiconst.CENTERRIGHT, width=text_width, height=row_height, state=uiconst.UI_PICKCHILDREN)
        self.label = Label(name='rewardView_label', parent=self.label_container, align=uiconst.CENTER, text=self.text, fontsize=scaled_font_size, fontstyle=STYLE_DEFAULT, state=uiconst.UI_PICKCHILDREN)

    def update_size(self, row_height, row_margin_icon, row_margin_internal, scale = 1.0):
        scaled_font_size = self._get_font_size(scale)
        scaled_icon_size = self._get_icon_size(scale)
        text_width = GetTextWidth(self.text, fontsize=scaled_font_size, fontStyle=STYLE_DEFAULT)
        self.width = scaled_icon_size + row_margin_icon + text_width
        self.left = row_margin_internal
        self.icon.width = scaled_icon_size
        self.icon.height = scaled_icon_size
        self.label_container.width = text_width
        self.label_container.height = row_height
        self.label.fontsize = scaled_font_size

    def _get_font_size(self, scale):
        return self.font_size * scale

    def _get_icon_size(self, scale):
        return self.icon_size * scale


class LpIconView(IconLabelView):
    IN_RW_CORP_STATION_LABEL = 'UI/ResourceWars/LPRewarded'
    __notifyevents__ = ['OnSessionChanged']

    def ApplyAttributes(self, attributes):
        self.rw_corp_id = attributes.rw_corp_id
        self.rw_svc = sm.GetService('rwService')
        super(LpIconView, self).ApplyAttributes(attributes)
        StartTasklet(self.setup_tooltip)
        sm.RegisterNotify(self)

    def _is_in_rw_corp_station(self):
        return self.rw_svc.is_rw_corp_station(self.rw_corp_id)

    def setup_tooltip(self):
        self.setup_lp_store_tooltip()
        if self._is_in_rw_corp_station():
            return
        rw_station_ids = sm.RemoteSvc('RWManager').get_closest_rw_stations(session.solarsystemid2)
        rw_station_id = rw_station_ids.get(self.rw_corp_id, None)
        if rw_station_id is not None:
            self.setup_rw_station_tooltip(rw_station_id)

    def setup_lp_store_tooltip(self):
        self.hint = GetByLabel(self.IN_RW_CORP_STATION_LABEL)
        self.tooltipPanelClassInfo = None
        self.OnClick = uicore.cmd.OpenLpstore

    def setup_rw_station_tooltip(self, rw_station_id):
        self.hint = None
        self.tooltipPanelClassInfo = LpIconViewTooltip(corporationID=self.rw_corp_id, stationID=rw_station_id)
        self.OnClick = None

    def OnMouseEnter(self, *args):
        super(LpIconView, self).OnMouseEnter(args)

    def OnMouseExit(self, *args):
        super(LpIconView, self).OnMouseExit(args)

    def OnSessionChanged(self, *args):
        StartTasklet(self.setup_tooltip)


class LpIconViewTooltip(TooltipBaseWrapper):
    NOT_IN_RW_CORP_STATION_LABEL = 'UI/ResourceWars/LPRewardedNotInStation'

    def __init__(self, *args, **optionalKeywordArguments):
        self.destroyed = False
        self.corporationID = optionalKeywordArguments.get('corporationID')
        self.stationID = optionalKeywordArguments.get('stationID')
        station = sm.GetService('ui').GetStationStaticInfo(self.stationID)
        self.stationSolarSystemID = station.solarSystemID
        self.stationTypeID = station.stationTypeID
        self.menuSvc = sm.GetService('menu')
        self._BuildText()
        super(LpIconViewTooltip, self).__init__(args, optionalKeywordArguments)

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        label = self.tooltipPanel.AddLabelMedium(text=self.text, state=uiconst.UI_NORMAL, wrapWidth=300)
        label.OnMouseDownWithUrl = self.OnMouseDownWithUrl
        return self.tooltipPanel

    def _GetStationLink(self):
        stationName = cfg.evelocations.Get(self.stationID).locationName
        stationLink = GetShowInfoLink(self.stationTypeID, stationName, itemID=self.stationID)
        return stationLink

    def _GetCorpLink(self):
        corporationName = cfg.eveowners.Get(self.corporationID).name
        return GetShowInfoLink(typeCorporation, corporationName, itemID=self.corporationID)

    def _BuildText(self):
        stationLink = self._GetStationLink()
        corpLink = self._GetCorpLink()
        self.text = GetByLabel(self.NOT_IN_RW_CORP_STATION_LABEL, stationLink=stationLink, corpLink=corpLink)

    def OnMouseDownWithUrl(self, url, *args):
        StartTasklet(self.ShowStationRadialMenu, url)

    def ShowStationRadialMenu(self, url):
        url = url.replace('showinfo:', '')
        ids = url.split('//')
        try:
            if len(ids) > 1:
                itemID = int(ids[1])
                if self.stationID == itemID:
                    self.menuSvc.TryExpandActionMenu(itemID=itemID, clickedObject=self, typeID=self.stationTypeID)
        except:
            log.LogTraceback('Failed to convert string to ids when opening station radial menu for link')
