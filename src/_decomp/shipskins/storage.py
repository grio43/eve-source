#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipskins\storage.py
from collections import defaultdict
from logging import getLogger
logger = getLogger(__name__)

class LicensedSkin(object):

    def __init__(self, skinID, expires = None, isSingleUse = False):
        self._skinID = skinID
        self._expires = expires
        self._isSingleUse = isSingleUse

    def __repr__(self):
        return "<LicensedSkin %s expires='%s' isSingleUse='%s'>" % (self._skinID, self._expires, self._isSingleUse)

    @property
    def skinID(self):
        return self._skinID

    @property
    def isSingleUse(self):
        return self._isSingleUse

    @isSingleUse.setter
    def isSingleUse(self, isSingleUse):
        self._isSingleUse = isSingleUse

    @property
    def expires(self):
        return self._expires

    def lastsLongerThan(self, other):
        if other is None:
            return True
        if other.expires is None:
            return False
        return self.expires is None or other.expires < self.expires


class Cache(dict):

    def __init__(self, get_func):
        super(Cache, self).__init__()
        self.get_func = get_func

    def __missing__(self, key):
        result = self[key] = self.get_func(key)
        return result


class LicensedSkinStorage(object):

    def __init__(self, clock):
        self.clock = clock
        self.skins_by_ownerid = Cache(self._get_licensed_skins_map)

    def is_skin_licensed(self, ownerID, skinID):
        if skinID is None:
            return True
        self._check_skin_expiry(ownerID, skinID)
        return skinID in self.skins_by_ownerid[ownerID]

    def is_skin_permanently_licensed(self, ownerID, skinID):
        if not self.is_skin_licensed(ownerID, skinID):
            return False
        skin = self.get_licensed_skin(ownerID, skinID)
        return skin.expires is None

    def is_skin_single_use(self, ownerID, skinID):
        if skinID not in self.skins_by_ownerid[ownerID]:
            return False
        skin = self.get_licensed_skin(ownerID, skinID)
        return skin.isSingleUse

    def add_licensed_skin(self, ownerID, skinID, duration, isSingleUse):
        self._check_skin_expiry(ownerID, skinID)
        skin = self.skins_by_ownerid[ownerID].get(skinID, None)
        if skin is not None and skin.expires is None:
            raise SkinAlreadyLicensed()
        if skin is None:
            new_skin = self._add_licensed_skin(ownerID, skinID, duration, isSingleUse)
        else:
            new_skin = self._update_licensed_skin(ownerID, skinID, duration, isSingleUse)
        self.skins_by_ownerid[ownerID][skinID] = new_skin

    def get_licensed_skins(self, ownerID):
        skins = self.skins_by_ownerid[ownerID].values()
        for skin in skins:
            self._check_skin_expiry(ownerID, skin.skinID)

        return self.skins_by_ownerid[ownerID].values()

    def get_single_use_skins(self, ownerID):
        return [ skin for skin in self.skins_by_ownerid[ownerID].values() if skin.isSingleUse ]

    def get_licensed_skin(self, ownerID, skinID):
        try:
            self._check_skin_expiry(ownerID, skinID)
            return self.skins_by_ownerid[ownerID][skinID]
        except KeyError:
            raise SkinNotLicensed()

    def remove_licensed_skin(self, ownerID, skinID):
        skins = self.skins_by_ownerid[ownerID]
        if skinID not in skins:
            raise KeyError()
        self._remove_licensed_skin(ownerID, skinID)
        del self.skins_by_ownerid[ownerID][skinID]

    def expire_licensed_skin(self, ownerID, skinID):
        return self._expire_licensed_skin(ownerID, skinID)

    def prime(self, ownerID):
        return self.skins_by_ownerid[ownerID]

    def unprime(self, ownerID):
        if ownerID in self.skins_by_ownerid:
            del self.skins_by_ownerid[ownerID]

    def check_all_skin_expiries(self, ownerID):
        expired_skin_ids = []
        for skinID in self.skins_by_ownerid[ownerID]:
            if self._check_skin_expiry(ownerID, skinID):
                expired_skin_ids.append(skinID)

        return expired_skin_ids

    def _check_skin_expiry(self, ownerID, skinID):
        skins = self.skins_by_ownerid[ownerID]
        if skinID not in skins:
            return False
        skin = skins[skinID]
        if skin.expires is not None and skin.expires < self.clock():
            self._remove_licensed_skin(ownerID, skinID)
            del self.skins_by_ownerid[ownerID]
            return True
        return False

    def _get_licensed_skins_map(self, ownerID):
        skins = self._get_licensed_skins(ownerID)
        return {skin.skinID:skin for skin in skins}

    def _add_licensed_skin(self, ownerID, skinID, duration, isSingleUse):
        raise NotImplementedError()

    def _update_licensed_skin(self, ownerID, skinID, duration, isSingleUse):
        raise NotImplementedError()

    def _get_licensed_skins(self, ownerID):
        raise NotImplementedError()

    def _remove_licensed_skin(self, ownerID, skinID):
        raise NotImplementedError()

    def _expire_licensed_skin(self, ownerID, skinID):
        raise NotImplementedError()


class AppliedSkinStorage(object):

    def __init__(self, licensed_skin_storage):
        self.licensed_skins = licensed_skin_storage
        self.applied_skins = Cache(self._get_applied_skins)

    def unprime(self, ownerID):
        if ownerID in self.applied_skins:
            del self.applied_skins[ownerID]

    def apply_skin(self, ownerID, skinID, itemID):
        if not self.licensed_skins.is_skin_licensed(ownerID, skinID):
            raise SkinNotLicensed()
        if skinID is None:
            self.clear_applied_skin(ownerID, itemID)
        else:
            self._insert_or_update(ownerID, skinID, itemID)

    def clear_applied_skin(self, ownerID, itemID):
        if itemID in self.applied_skins[ownerID]:
            previous = self.applied_skins[ownerID][itemID]
            self._remove_applied_skin(ownerID, itemID)
            del self.applied_skins[ownerID][itemID]
            logger.info('SKIN STATES - Storage: cleared applied 1st party skin for character %s, ship %s: %s', ownerID, itemID, previous)

    def get_items_by_skin_applied(self, ownerID):
        itemsBySkin = defaultdict(set)
        unapplications = []
        for itemID in self.applied_skins[ownerID]:
            skinID = self.applied_skins[ownerID][itemID]
            itemsBySkin[skinID].add(itemID)
            if not self.licensed_skins.is_skin_licensed(ownerID, skinID):
                unapplications.append((ownerID, itemID))

        for ownerID, itemID in unapplications:
            self.clear_applied_skin(ownerID, itemID)

        return itemsBySkin

    def get_applied_skin_id(self, ownerID, itemID):
        if itemID not in self.applied_skins[ownerID]:
            return
        skinID = self.applied_skins[ownerID][itemID]
        if not self.licensed_skins.is_skin_licensed(ownerID, skinID):
            self._remove_applied_skin(ownerID, itemID)
            skinID = None
        return skinID

    def _insert_or_update(self, ownerID, skinID, itemID):
        if itemID in self.applied_skins[ownerID]:
            self._update_applied_skin(ownerID, skinID, itemID)
        else:
            self._insert_applied_skin(ownerID, skinID, itemID)
        self.applied_skins[ownerID][itemID] = skinID
        logger.info('SKIN STATES - Storage: applied 1st party skin for character %s, ship %s: %s', ownerID, itemID, skinID)

    def _get_applied_skins(self, ownerID):
        raise NotImplementedError()

    def _insert_applied_skin(self, ownerID, skinID, itemID):
        raise NotImplementedError()

    def _update_applied_skin(self, ownerID, skinID, itemID):
        raise NotImplementedError()

    def _remove_applied_skin(self, ownerID, itemID):
        raise NotImplementedError()


class SkinNotLicensed(Exception):
    pass


class SkinAlreadyLicensed(Exception):
    pass
