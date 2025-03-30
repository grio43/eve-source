#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\chip_group.py
import eveui
from carbonui.uicore import uicore
from raffles.client.localization import Text
from .chip import Chip

class ChipGroup(eveui.Container):
    default_name = 'ChipGroup'

    def __init__(self, on_clear_all, **kwargs):
        super(ChipGroup, self).__init__(**kwargs)
        self._on_clear_all = on_clear_all
        self._multi_chip = MultiChip(parent=self, on_clear=self._on_clear_all)
        self._chips_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_left)
        self._chips_container._OnResize = self._check_clipping

    def add_chip(self, chip):
        chip.SetParent(self._chips_container)

    def _check_clipping(self):
        clipped = self._chips_container.IsPartiallyClipped(self)
        if clipped:
            self._show_multi_chip()
        else:
            self._show_all_chips()

    def _show_all_chips(self):
        self._multi_chip.clear()
        self._chips_container.state = eveui.State.pick_children
        self._chips_container.opacity = 1

    def _show_multi_chip(self):
        self._multi_chip.update(self._chips_container.children)
        self._chips_container.state = eveui.State.disabled
        self._chips_container.opacity = 0


class MultiChip(Chip):
    default_name = 'MultiChip'
    default_align = eveui.Align.to_left_no_push
    _chips = []
    _tooltip_chips = {}

    def clear(self):
        super(MultiChip, self).clear()
        self._chips = []
        self._tooltip_chips.clear()
        uicore.uilib.tooltipHandler.RefreshTooltipForOwner(self)

    def update(self, chips):
        self._chips = []
        for chip in chips:
            if chip.text:
                self._chips.append(chip)
            else:
                tooltip_chip = self._tooltip_chips.pop(chip, None)
                if tooltip_chip:
                    tooltip_chip.Close()

        self.text = Text.multi_chip(count=len(self._chips))

    def LoadTooltipPanel(self, tooltip_panel, *args):
        if len(self._chips) == 0:
            return
        tooltip_panel.LoadGeneric1ColumnTemplate()
        tooltip_panel.SetState(eveui.State.normal)
        tooltip_panel.margin = 4
        container = eveui.ContainerAutoSize(width=194)
        tooltip_panel.AddCell(container)
        self._tooltip_chips.clear()
        for chip in self._chips:
            chip_container = eveui.Container(parent=container, align=eveui.Align.to_top, height=28, padding=(0, 2, 0, 2))
            self._tooltip_chips[chip] = chip_container
            Chip(parent=chip_container, on_clear=chip._on_clear, text=chip.text, align=eveui.Align.to_all, padding=0)
