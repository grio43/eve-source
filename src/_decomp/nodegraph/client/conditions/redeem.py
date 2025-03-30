#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\redeem.py
import evetypes
from nodegraph.common.util import get_object_predicate
from nodegraph.client.util import get_item_name
from .base import Condition

class ItemInRedeemingQueue(Condition):
    atom_id = 562

    def __init__(self, type_id = None, group_id = None, category_id = None, **kwargs):
        super(ItemInRedeemingQueue, self).__init__(**kwargs)
        self.type_id = type_id
        self.group_id = group_id
        self.category_id = category_id

    def validate(self, **kwargs):
        redeem_tokens = sm.GetService('redeem').GetRedeemTokens()
        if self.type_id:
            predicate = get_object_predicate('typeID', self.type_id)
        elif self.group_id:
            group_id = self.group_id

            def predicate_function(item):
                return evetypes.GetGroupID(item.typeID) == group_id

            predicate = predicate_function
        elif self.category_id:
            category_id = self.category_id

            def predicate_function(item):
                return evetypes.GetCategoryID(item.typeID) == category_id

            predicate = predicate_function
        else:
            return bool(redeem_tokens)
        for token in redeem_tokens:
            if predicate(token):
                return True

        return False

    @classmethod
    def get_subtitle(cls, **kwargs):
        return get_item_name(**kwargs)
