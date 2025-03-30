#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\link\validators\paste.py
import re
from carbon.common.script.util.commonutils import StripTags
from chat.client.local_chat.validators.paste import PasteValidator

class ShipSkinLinkValidator(PasteValidator):

    def sanitize_match(self, match):
        start_tag = match.groups()[0]
        link_name = match.groups()[1]
        end_tag = match.groups()[2]
        link_name_no_tags = StripTags(link_name)
        return u'{0}{1}{2}'.format(start_tag, link_name_no_tags, end_tag)


class ShipSkinDesignLinkValidator(ShipSkinLinkValidator):

    def validate(self, text):
        try:
            pattern = re.compile('(<a href=\\"shipSkinDesign:\\d+/[a-z0-9-]+\\">)(.+)(</a>)')
            link = re.match(pattern, text)
            if link:
                return self.sanitize_match(link)
            return None
        except:
            return None


class ShipSkinListingLinkValidator(ShipSkinLinkValidator):

    def validate(self, text):
        try:
            pattern = re.compile('(<a href=\\"shipSkinListing:[a-z0-9-]+\\">)(.+)(</a>)')
            link = re.match(pattern, text)
            if link:
                return self.sanitize_match(link)
            return None
        except:
            return None
