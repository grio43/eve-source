#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\arguments.py


class Arguments(object):

    def __init__(self, blue_args):
        self._blue_args = blue_args
        self.values_by_key = {}
        self.args = set()
        self._parse_args(blue_args)

    def _parse_args(self, blue_args):
        for arg in blue_args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.values_by_key[key] = value
            elif ':' in arg:
                key, value = arg.split(':', 1)
                self.values_by_key[key] = value
            else:
                self.args.add(arg)

    def has_argument(self, arg):
        if arg in self.values_by_key:
            return True
        if arg in self.args:
            return True
        return False

    def get_string_value(self, key):
        if key not in self.values_by_key:
            raise KeyNotInArgs()
        return self.values_by_key[key]

    def get_int_value(self, key):
        return int(self.get_string_value(key))


class KeyNotInArgs(Exception):
    pass
