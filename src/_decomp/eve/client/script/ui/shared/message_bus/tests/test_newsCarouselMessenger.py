#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\message_bus\tests\test_newsCarouselMessenger.py
from eve.client.script.ui.shared.message_bus.newsCarouselMessenger import NewsCarouselMessenger
from testsuites.testcases import ClientTestCase
from mock import MagicMock

class TestNewsCarouselMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestNewsCarouselMessengerCompatibility, self).setUp()
        self.mb = NewsCarouselMessenger(MagicMock())

    def test_displayed(self):
        news_id = 1
        self.mb.displayed(news_id)

    def test_acknowledged(self):
        news_id = 1
        self.mb.acknowledged(news_id)

    def test_auto_popup_toggled(self):
        checked = 1
        self.mb.auto_popup_toggled(checked)
