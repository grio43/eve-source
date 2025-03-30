#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\contracts\link.py
SCHEME = 'contract'

def register_link_handlers(registry):
    registry.register(SCHEME, handle_contract_link, hint='UI/Contracts/ShowContract')


def handle_contract_link(url):
    solar_system_id, contract_id = parse_contract_url(url)
    sm.GetService('contracts').ShowContract(contract_id)


def parse_contract_url(url):
    content = url[url.index(':') + 1:]
    solar_system_id, contract_id = content.split('//')
    return (int(solar_system_id), int(contract_id))


def format_contract_url(solar_system_id, contract_id):
    return u'{}:{}//{}'.format(SCHEME, solar_system_id, contract_id)
