#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\show_info\parse.py
import logging
import evetypes
import gametime
import inventorycommon.const as invconst
import utillib
log = logging.getLogger(__name__)

def parse_show_info_url(url):
    return ShowInfoLinkData.parse(url)


class ShowInfoLinkData(object):

    def __init__(self, type_id, item_id = None, abstract_info = None, bookmark_info = None):
        self.type_id = type_id
        self.item_id = item_id
        self.abstract_info = abstract_info
        self.bookmark_info = bookmark_info

    @classmethod
    def parse(cls, url):
        url_without_scheme = url[url.index(':') + 1:]
        parts = url_without_scheme.split('//')
        type_id = int(parts[0])
        item_id = None
        if len(parts) > 1:
            try:
                item_id = int(parts[1])
                if item_id == 0:
                    item_id = None
            except ValueError:
                pass

        abstract_info = None
        bookmark_info = None
        if len(parts) > 2:
            category_id = evetypes.GetCategoryID(type_id)
            if category_id == invconst.categoryShip:
                abstract_info = utillib.KeyVal(ownerID=int(parts[2]))
            elif type_id == invconst.typeCertificate:
                abstract_info = utillib.KeyVal(certificateID=item_id)
            elif category_id == invconst.categoryBlueprint:
                try:
                    abstract_info = utillib.KeyVal(category_id=category_id, runs=int(parts[2]), isCopy=bool(int(parts[3])), productivityLevel=int(parts[4]), materialLevel=int(parts[5]))
                except Exception:
                    log.warning('Failed to parse blueprint abstract info from url {}'.format(url))

            else:
                agent_ids = [ int(agent_id) for agent_id in parts[5].split(',') ]
                bookmark_info = utillib.KeyVal(ownerID=session.charid, itemID=item_id, typeID=type_id, flag=None, memo='', created=gametime.GetWallclockTime(), x=float(parts[2]), y=float(parts[3]), z=float(parts[4]), locationID=item_id, agentID=agent_ids[0], referringAgentID=agent_ids[1] if len(agent_ids) > 1 else None, locationNumber=int(parts[6]), locationType=parts[7], deadspace=int(parts[7] in ('dungeon', 'agenthomebase')))
        return cls(type_id, item_id, abstract_info, bookmark_info)
