#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\effects.py
from .base import Action
from logging import getLogger
logger = getLogger(__name__)

class LoadBoardShipEffects(Action):
    atom_id = 245

    def __init__(self, item_id = None, **kwargs):
        super(LoadBoardShipEffects, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(LoadBoardShipEffects, self).start(**kwargs)
        if self.item_id:
            sm.GetService('FxSequencer').OnSpecialFX(shipID=self.item_id, moduleID=None, moduleTypeID=None, targetID=None, otherTypeID=None, guid='effects.NPEBoardShip', isOffensive=False, start=1, active=True, graphicInfo={'board': '0',
             'playerShip': '{item_id}'.format(item_id=self.item_id)})


class StartBoardShipEffects(Action):
    atom_id = 246

    def __init__(self, item_id = None, **kwargs):
        super(StartBoardShipEffects, self).__init__(**kwargs)
        self.item_id = item_id

    def start(self, **kwargs):
        super(StartBoardShipEffects, self).start(**kwargs)
        if self.item_id:
            sm.GetService('FxSequencer').OnSpecialFX(shipID=self.item_id, moduleID=None, moduleTypeID=None, targetID=None, otherTypeID=None, guid='effects.NPEBoardShip', isOffensive=False, start=1, active=True, graphicInfo={'board': '1',
             'playerShip': '{item_id}'.format(item_id=self.item_id)})


class SetGraphicsControllerVariable(Action):
    atom_id = 418

    def __init__(self, key = None, value = None, item_id = None, **kwargs):
        super(SetGraphicsControllerVariable, self).__init__(**kwargs)
        self.key = key
        self.value = value
        self.item_id = item_id

    def _log_success(self, key, value, ball):
        from evetypes import GetEnglishName
        item_id = ball.id
        type_id = ball.typeID
        logger.debug(u"Set Graphics Controller Variable {key}={value} on '{name}' (itemID: {item_id}, typeID: {type_id})".format(key=key, value=value, name=GetEnglishName(type_id) if type_id else 'None', item_id=item_id, type_id=type_id))

    def start(self, **kwargs):
        super(SetGraphicsControllerVariable, self).start(**kwargs)
        if not self.key or not self.item_id:
            return
        ball = sm.GetService('michelle').GetBallAndWaitForModel(self.item_id)
        if ball:
            key = str(self.key)
            value = self.value or 0.0
            ball.SetControllerVariable(key, value)
            self._log_success(key, value, ball)

    @classmethod
    def get_subtitle(cls, key = None, value = None, **kwargs):
        return '{}={}'.format(key, value or 0)
