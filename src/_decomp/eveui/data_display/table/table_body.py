#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\table_body.py
import eveui

class TableBody(eveui.ScrollContainer):
    default_name = 'TableBody'

    def __init__(self, data = None, item_height = 36, **kwargs):
        super(TableBody, self).__init__(**kwargs)
