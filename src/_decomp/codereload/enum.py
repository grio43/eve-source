#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\codereload\enum.py


def reloadable_enum(_cls = None, allow_override = False):

    def deco(cls):
        if not allow_override and hasattr(cls, '__reload_update__'):
            import warnings
            warnings.warn("Overriding a __reload_update__ hook\n\n{cls} already has a __reload_update__ hook defined. @reloadable_enum will completely replace that hook with its own. If this is what you want then you can pass 'allow_override=True' to the decorator in order to suppress this warning, like this:\n\n    @reloadable_enum(allow_override=True)\n    class {cls}(...):\n        ...\n".format(cls=cls.__name__))

        def reload_update(old_cls, _old_instance = None):
            if _old_instance is not None:
                return _old_instance
            from codereload.xreload import _update, deferred_update_global_references
            ignore = {'_member_map_', '_member_names_', '_value2member_map_'}
            for name, item in cls.__dict__.items():
                if name in ignore or isinstance(item, cls):
                    continue
                setattr(old_cls, name, _update(old_cls.__dict__.get(name, None), item))

            old_names = set(old_cls._member_names_)
            new_names = set(cls._member_names_)
            all_names = old_names.union(new_names)
            added_names = new_names - old_names
            removed_names = old_names - new_names
            for name in all_names:
                if name in removed_names:
                    old_cls._member_names_.remove(name)
                    del old_cls._value2member_map_[old_cls._member_map_[name].value]
                    del old_cls._member_map_[name]
                elif name in added_names:
                    old_cls._member_names_.append(name)
                    new_item = cls._member_map_[name]
                    new_item.__class__ = old_cls
                    old_cls._member_map_[name] = new_item
                    old_cls._value2member_map_[new_item.value] = new_item
                else:
                    del old_cls._value2member_map_[old_cls._member_map_[name].value]
                    new_item = cls._member_map_[name]
                    old_item = old_cls._member_map_[name]
                    old_item._value_ = new_item._value_
                    old_cls._value2member_map_[new_item.value] = old_item

            deferred_update_global_references(cls, old_cls)
            return old_cls

        setattr(cls, '__reload_update__', reload_update)
        return cls

    if _cls is not None:
        return deco(_cls)
    else:
        return deco
