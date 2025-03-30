#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\fixedButtonExtension.py
import abc
import signals
import weakref

class FixedButtonExtension(object):
    __metaclass__ = abc.ABCMeta

    @property
    def on_visible_changed(self):
        if not hasattr(self, '_on_visible_changed'):
            self._on_visible_changed = signals.Signal(signalName='_on_visible_changed')
        return self._on_visible_changed

    @abc.abstractproperty
    def is_visible(self):
        pass

    @abc.abstractmethod
    def create_button_data(self, parent):
        pass


class UnseenItemsExtension(FixedButtonExtension):

    def __init__(self, button_data_class, get_badge_count):
        self._button_data_ref = None
        self.button_data_class = button_data_class
        self.get_badge_count = get_badge_count

    @property
    def is_visible(self):
        return False

    def create_button_data(self, parent):
        old_button_data = self.button_data
        is_blinking = bool(self.get_badge_count())
        if old_button_data is not None:
            is_blinking = old_button_data.IsBlinking()
        self.button_data = self.button_data_class(parent=parent, isBlinking=is_blinking)

    @property
    def button_data(self):
        if self._button_data_ref is None:
            return
        return self._button_data_ref()

    @button_data.setter
    def button_data(self, data):
        self._button_data_ref = weakref.ref(data)

    def on_items_changed(self):
        self._update_badge_count()

    def _update_badge_count(self):
        if self.button_data and self.button_data:
            self.button_data.on_badge_count_changed()

    def connect_item_changes(self, on_items_changed):
        on_items_changed.connect(self.on_items_changed)

    def disconnect_item_changes(self, on_items_changed):
        on_items_changed.disconnect(self.on_items_changed)

    def reset_badge_count(self):
        if self.button_data and self.button_data:
            self.button_data.on_badge_count_changed()


class UnseenItemsExtensionForExistingButton(UnseenItemsExtension):

    def __init__(self, button_data_class, get_badge_count, button_id):
        super(UnseenItemsExtensionForExistingButton, self).__init__(button_data_class, get_badge_count)
        self.set_button_data_from_id(button_id)

    def set_button_data_from_id(self, button_id):
        self.button_data = sm.GetService('neocom').GetBtnData(button_id)


class OnlyShowWhenUnseenExtension(UnseenItemsExtension):

    def __init__(self, button_data_class, get_badge_count):
        super(OnlyShowWhenUnseenExtension, self).__init__(button_data_class, get_badge_count)
        self._was_visible = self.is_visible

    @property
    def is_visible(self):
        return self.get_badge_count() > 0

    def on_items_changed(self):
        super(OnlyShowWhenUnseenExtension, self).on_items_changed()
        self._update_visibility()

    def _update_visibility(self):
        if self.is_visible and not self._was_visible:
            self._was_visible = True
            self.on_visible_changed(self)
        elif self._was_visible and not self.is_visible:
            self._was_visible = False
            self.on_visible_changed(self)


class OnlyShowWhenAvailableExtension(OnlyShowWhenUnseenExtension):

    def __init__(self, button_data_class, get_badge_count, get_item_count):
        self.get_item_count = get_item_count
        super(OnlyShowWhenAvailableExtension, self).__init__(button_data_class, get_badge_count)

    @property
    def is_visible(self):
        return self.get_item_count() > 0


class EmptyItemStorage(object):

    def __init__(self):
        self.on_items_changed = signals.Signal(signalName='on_items_changed')
        self.on_items_changed.connect(self.update_unseen_count)
        self._unseen_count = None

    def get_unseen(self):
        return set()

    def _get_unseen_count(self):
        return len(self.get_unseen())

    def has_unseen(self):
        return self._get_unseen_count() > 0

    @property
    def unseen_count(self):
        if self._unseen_count is None:
            self.update_unseen_count()
        return self._unseen_count

    def update_unseen_count(self):
        old_unseen_count = self._unseen_count
        self._unseen_count = self._get_unseen_count()
        if old_unseen_count != self._unseen_count:
            self.on_items_changed()

    def mark_all_seen(self):
        pass


class SeenItemStorage(EmptyItemStorage):

    def __init__(self, get_items_function, settings_container, settings_key, start_as_seen = False):
        self.get_items = get_items_function
        self.settings_container = settings_container
        self.settings_key = settings_key
        super(SeenItemStorage, self).__init__()
        seen_items = self.settings_container.Get(self.settings_key, None)
        if start_as_seen and seen_items is None:
            self.mark_all_seen()

    def get_unseen(self):
        items = self.get_items()
        return items.difference(self.seen_items)

    def mark_all_seen(self):
        self.seen_items = self.get_items()

    def mark_all_unseen(self):
        self.seen_items = set()
        self.update_unseen_count()

    @property
    def seen_items(self):
        return self.settings_container.Get(self.settings_key, set())

    @seen_items.setter
    def seen_items(self, items):
        if len(self.seen_items.symmetric_difference(items)) == 0:
            return
        self.settings_container.Set(self.settings_key, set(items))
        self.on_items_changed()
        sm.GetService('settings').SaveSettings()

    def clear_all(self):
        self.settings_container.Set(self.settings_key, set())
        self.on_items_changed()
        sm.GetService('settings').SaveSettings()

    def mark_as_seen(self, item):
        new_seen_items = set(self.seen_items)
        new_seen_items.add(item)
        self.seen_items = new_seen_items
        self.update_unseen_count()

    def mark_as_unseen(self, item):
        if item in self.seen_items:
            new_seen_items = set(self.seen_items)
            new_seen_items.remove(item)
            self.seen_items = new_seen_items
        self.update_unseen_count()

    def mark_many_as_unseen(self, items):
        self.seen_items = set(self.seen_items).difference(set(items))
        self.update_unseen_count()


class UnseenItemStorage(EmptyItemStorage):

    def __init__(self, get_items_function, settings_container, settings_key, start_as_seen = False):
        self.get_items = get_items_function
        self.settings_container = settings_container
        self.settings_key = settings_key
        super(UnseenItemStorage, self).__init__()
        unseen_items = self.settings_container.Get(self.settings_key, None)
        if start_as_seen and unseen_items is None:
            self.mark_all_seen()

    def get_unseen(self):
        return self.unseen_items

    def mark_all_seen(self):
        self.unseen_items = set()
        self.update_unseen_count()

    def mark_all_unseen(self):
        self.unseen_items = self.get_items()
        self.update_unseen_count()

    @property
    def unseen_items(self):
        return self.settings_container.Get(self.settings_key, set())

    @unseen_items.setter
    def unseen_items(self, items):
        if len(self.unseen_items.symmetric_difference(items)) == 0:
            return
        self.settings_container.Set(self.settings_key, set(items))
        self.on_items_changed()
        sm.GetService('settings').SaveSettings()

    def mark_as_seen(self, item):
        if item in self.unseen_items:
            new_unseen_items = set(self.unseen_items)
            new_unseen_items.remove(item)
            self.unseen_items = new_unseen_items
            self.update_unseen_count()

    def mark_as_unseen(self, item):
        new_unseen_items = set(self.unseen_items)
        new_unseen_items.add(item)
        self.unseen_items = new_unseen_items
        self.update_unseen_count()

    def update_unseen_count(self):
        old_unseen_count = self._unseen_count
        self._unseen_count = self._get_unseen_count()
        if old_unseen_count != self._unseen_count:
            self.on_items_changed()


class SeenItemMultipleLocationsStorage(EmptyItemStorage):

    def __init__(self, settings_container):
        self.settings_container = settings_container
        super(SeenItemMultipleLocationsStorage, self).__init__()
        self.location_storages = {}

    def has_location(self, location_id):
        return location_id in self.location_storages.keys()

    def add_location_storage(self, location_id, item_getter, setting_key):
        self.location_storages[location_id] = UnseenItemStorage(get_items_function=item_getter, settings_container=self.settings_container, settings_key=setting_key, start_as_seen=True)
        self.location_storages[location_id].on_items_changed.connect(self.on_items_changed)

    def get_unseen(self):
        return set().union(*[ storage.get_unseen() for storage in self.location_storages.values() ])

    def mark_all_seen(self):
        for storage in self.location_storages.values():
            storage.mark_all_seen()

    def mark_seen_in_location(self, location_id):
        if location_id in self.location_storages:
            self.location_storages[location_id].mark_all_seen()
        super(SeenItemMultipleLocationsStorage, self).update_unseen_count()

    def has_unseen_items_in_location(self, location_id):
        if location_id not in self.location_storages:
            return False
        return self.location_storages[location_id].unseen_count > 0

    def mark_all_seen_in_location(self, location_id):
        if location_id in self.location_storages:
            self.location_storages[location_id].mark_all_seen()

    def mark_as_seen(self, item_id):
        for storage in self.location_storages.values():
            storage.mark_as_seen(item_id)

        self.update_unseen_count()

    def update_unseen_count(self):
        for storage in self.location_storages.values():
            storage.update_unseen_count()

        super(SeenItemMultipleLocationsStorage, self).update_unseen_count()

    def update_unseen_count_in_location(self, location_id):
        if location_id in self.location_storages:
            self.location_storages[location_id].update_unseen_count()
            super(SeenItemMultipleLocationsStorage, self).update_unseen_count()

    def is_unseen(self, item_id):
        return item_id in self.get_unseen()

    def mark_as_seen_in_location(self, item_id, location):
        if location:
            _, _, location_id = location
            if location_id in self.location_storages:
                self.location_storages[location_id].mark_as_seen(item_id)
                return
        self.mark_as_seen(item_id)

    def mark_as_unseen_in_location(self, item_id, location):
        if location:
            _, _, location_id = location
            if location_id in self.location_storages:
                self.location_storages[location_id].mark_as_unseen(item_id)

    def remove_obsolete_unseen(self):
        for storage in self.location_storages.values():
            all_items = storage.get_items()
            all_unseen = storage.unseen_items
            actual_unseen = all_items.intersection(all_unseen)
            storage.unseen_items = actual_unseen


class AmountStorage(SeenItemStorage):

    def get_unseen(self):
        return self.calculate_unseen(self.get_items())

    def _get_unseen_count(self):
        return self.get_unseen()

    @property
    def seen_items(self):
        return self.settings_container.Get(self.settings_key, None)

    @seen_items.setter
    def seen_items(self, items):
        if self.seen_items == items:
            return
        self.settings_container.Set(self.settings_key, items)
        self.on_items_changed()

    def update_items(self, items):
        old_unseen_count = self._unseen_count
        self._unseen_count = self.calculate_unseen(items)
        if old_unseen_count != self._unseen_count:
            self.on_items_changed()

    def calculate_unseen(self, items):
        return max(0, min(1, items - self.seen_items))

    def mark_amount_as_seen(self, amount):
        self.seen_items = amount
        self.update_unseen_count()

    def mark_as_seen(self, item):
        self.update_unseen_count()

    def mark_as_unseen(self, item):
        self.update_unseen_count()
