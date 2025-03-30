#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\message_bus\newsCarouselMessenger.py
from eveProto.generated.eve_public.app.eveonline.newscarousel.ui.ui_pb2 import Displayed
from eveProto.generated.eve_public.app.eveonline.newscarousel.ui.ui_pb2 import Acknowledged
from eveProto.generated.eve_public.app.eveonline.newscarousel.ui.ui_pb2 import AutoPopupToggled

class NewsCarouselMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def displayed(self, news_id):
        event = Displayed()
        event.news = int(news_id)
        self.public_gateway.publish_event_payload(event)

    def acknowledged(self, news_id):
        event = Acknowledged()
        event.news = int(news_id)
        self.public_gateway.publish_event_payload(event)

    def auto_popup_toggled(self, checked):
        event = AutoPopupToggled()
        event.checked = checked
        self.public_gateway.publish_event_payload(event)
