#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\agencyEventLog.py
import eveexceptions
from eve.client.script.ui.shared.agencyNew.message_bus.agencyMessenger import AgencyMessenger

@eveexceptions.EatsExceptions('protoClientLogs')
def LogEventCardClicked(content_piece):
    message_bus = AgencyMessenger(sm.GetService('publicGatewaySvc'))
    content_id = int(content_piece.GetContentTypeID() or 0)
    num_jumps = int(content_piece.GetJumpsToSelfFromCurrentLocation() or 0)
    security_status = float(content_piece.GetSystemSecurityStatus() or 0.0)
    message_bus.content_card_clicked(content_id, num_jumps, security_status)


@eveexceptions.EatsExceptions('protoClientLogs')
def LogEventGroupCardClicked(content_group):
    message_bus = AgencyMessenger(sm.GetService('publicGatewaySvc'))
    group_id = int(content_group.GetID() or 0)
    message_bus.group_card_clicked(group_id)


@eveexceptions.EatsExceptions('protoClientLogs')
def LogEventPrimaryButtonClick(content_piece, action_id):
    message_bus = AgencyMessenger(sm.GetService('publicGatewaySvc'))
    action_id = int(action_id or 0)
    content_id = int(content_piece.GetContentTypeID() or 0)
    message_bus.action_taken(action_id, content_id)


@eveexceptions.EatsExceptions('protoClientLogs')
def LogEventFilterChanged(content_group_id, filter_type, filter_value):
    message_bus = AgencyMessenger(sm.GetService('publicGatewaySvc'))
    filter_id = int(filter_type or 0)
    group_id = int(content_group_id or 0)
    filter_value = int(filter_value or 0)
    message_bus.filter_changed(filter_id, group_id, filter_value)


@eveexceptions.EatsExceptions('protoClientLogs')
def LogEventBookmarkAdded(content_group_id):
    message_bus = AgencyMessenger(sm.GetService('publicGatewaySvc'))
    group_id = int(content_group_id or 0)
    message_bus.bookmark_added(group_id)
