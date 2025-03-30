#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\message_bus\tests\test_agencyMessenger.py
from eve.client.script.ui.shared.agencyNew.message_bus.agencyMessenger import AgencyMessenger
from testsuites.testcases import ClientTestCase
from mock import MagicMock

class TestAgencyMessengerCompatibility(ClientTestCase):

    def setUp(self):
        super(TestAgencyMessengerCompatibility, self).setUp()
        self.mb = AgencyMessenger(MagicMock())

    def test_action_taken(self):
        action_id = 1
        content_id = 1
        self.mb.action_taken(action_id, content_id)

    def test_bookmark_added(self):
        group_id = 1
        self.mb.bookmark_added(group_id)

    def test_filter_changed(self):
        filter_id = 1
        group_id = 1
        filter_value = 1
        self.mb.filter_changed(filter_id, group_id, filter_value)

    def test_content_card_clicked(self):
        content_id = 1
        num_jumps = 1
        security_status = 5.23
        self.mb.content_card_clicked(content_id, num_jumps, security_status)

    def test_group_card_clicked(self):
        group_id = 1
        self.mb.group_card_clicked(group_id)

    def test_video_link_created(self):
        video_path = 'my_video_path'
        self.mb.help_video_link_created(video_path)

    def test_video_link_clicked(self):
        video_path = 'my_video_path'
        self.mb.help_video_link_created(video_path)
