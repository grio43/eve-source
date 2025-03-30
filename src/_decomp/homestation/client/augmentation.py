#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\augmentation.py
import caching
import dogma.const
import signals
import uthread2
from carbon.common.script.sys.serviceManager import ServiceManager

class Augmentations(object):
    __notifyevents__ = ('OnBoosterUpdated', 'OnImplantsChanged', 'OnItemChange')

    def __init__(self, character_id, godma):
        self.on_update = signals.Signal()
        self._character_id = character_id
        self._godma = godma
        self._augmentations = None
        ServiceManager.Instance().RegisterNotify(self)

    @property
    def augmentations(self):
        if self._augmentations is None:
            self.load()
        return self._augmentations

    @property
    def has_destructible_augmentations(self):
        return any((augmentation.is_destructible for augmentation in self.augmentations))

    def load(self):
        character = self._get_character_from_godma(self._character_id)
        implants = [ Augmentation(type_id=implant.typeID, godma=self._godma) for implant in character.implants ]
        boosters = [ Augmentation(type_id=booster.typeID, godma=self._godma) for booster in character.boosters ]
        self._augmentations = implants + boosters

    def _get_character_from_godma(self, character_id, retries_max = 30):
        character = self._godma.GetItem(character_id)
        if character:
            return character
        retry_count = 0
        while not character and retry_count <= retries_max:
            uthread2.sleep(0.1)
            character = self._godma.GetItem(character_id)
            retry_count += 1

        if not character:
            raise RuntimeError('Failed to retrieve character from Godma')
        return character

    def _handle_augmentations_changed(self):
        self._augmentations = None
        self.on_update()

    def OnImplantsChanged(self):
        self._handle_augmentations_changed()

    def OnBoosterUpdated(self):
        self._handle_augmentations_changed()


class Augmentation(object):

    def __init__(self, type_id, godma):
        self.type_id = type_id
        self._godma = godma

    @caching.lazy_property
    def is_destructible(self):
        return not bool(self._godma.GetTypeAttribute2(self.type_id, dogma.const.attributeNonDestructible))
