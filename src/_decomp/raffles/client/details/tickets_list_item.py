#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\tickets_list_item.py
import eveui
from .ticket import Ticket

class TicketsListItem(eveui.FlowContainer):
    default_align = eveui.Align.to_top
    default_height = 30
    default_padBottom = 28

    def __init__(self, ticket_controllers, **kwargs):
        super(TicketsListItem, self).__init__(centerContent=True, contentSpacing=(28, 0), **kwargs)
        self.controllers = ticket_controllers
        self._tickets = []
        self._layout()

    def update_item(self, index):
        if index is None:
            self.state = eveui.State.hidden
            return
        self.state = eveui.State.pick_children
        ticket_index = index * 4
        for i, ticket in enumerate(self._tickets):
            if ticket_index < len(self.controllers):
                ticket.set_ticket_controller(self.controllers[ticket_index])
            else:
                ticket.state = eveui.State.hidden
            ticket_index += 1

    def _layout(self):
        for i in range(4):
            self._tickets.append(Ticket(parent=self))
