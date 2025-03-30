#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecrypto\settings.py


def get_boot():
    from eveprefs import boot
    if boot is not None:
        return boot
    import eveprefs
    from eveprefs.inmemory import InMemoryIniFile
    return eveprefs.Handler(InMemoryIniFile(role=''))


boot = get_boot()
cryptoPack = boot.GetValue('cryptoPack', 'Placebo')
