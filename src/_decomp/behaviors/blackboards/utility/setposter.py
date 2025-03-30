#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\blackboards\utility\setposter.py


class SetPoster(object):

    def __init__(self, channel):
        self.channel = channel

    def entry_added(self, entry):
        _set = self.channel.GetLastMessageValue()
        if _set is None:
            _set = {entry}
        elif entry not in _set:
            _set.add(entry)
        else:
            return False
        self.channel.SendMessage(_set)
        return True

    def entry_removed(self, entry):
        _set = self.channel.GetLastMessageValue()
        if not _set:
            return False
        if entry not in _set:
            return False
        _set.discard(entry)
        return True
