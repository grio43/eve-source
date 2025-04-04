#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\cherrypy\_cpchecker.py
import os
import warnings
import cherrypy
from cherrypy._cpcompat import iteritems, copykeys, builtins

class Checker(object):
    on = True

    def __init__(self):
        self._populate_known_types()

    def __call__(self):
        if self.on:
            oldformatwarning = warnings.formatwarning
            warnings.formatwarning = self.formatwarning
            try:
                for name in dir(self):
                    if name.startswith('check_'):
                        method = getattr(self, name)
                        if method and hasattr(method, '__call__'):
                            method()

            finally:
                warnings.formatwarning = oldformatwarning

    def formatwarning(self, message, category, filename, lineno, line = None):
        return 'CherryPy Checker:\n%s\n\n' % message

    global_config_contained_paths = False

    def check_app_config_entries_dont_start_with_script_name(self):
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            if not app.config:
                continue
            if sn == '':
                continue
            sn_atoms = sn.strip('/').split('/')
            for key in app.config.keys():
                key_atoms = key.strip('/').split('/')
                if key_atoms[:len(sn_atoms)] == sn_atoms:
                    warnings.warn('The application mounted at %r has config entries that start with its script name: %r' % (sn, key))

    def check_site_config_entries_in_app_config(self):
        for sn, app in iteritems(cherrypy.tree.apps):
            if not isinstance(app, cherrypy.Application):
                continue
            msg = []
            for section, entries in iteritems(app.config):
                if section.startswith('/'):
                    for key, value in iteritems(entries):
                        for n in ('engine.', 'server.', 'tree.', 'checker.'):
                            if key.startswith(n):
                                msg.append('[%s] %s = %s' % (section, key, value))

            if msg:
                msg.insert(0, 'The application mounted at %r contains the following config entries, which are only allowed in site-wide config. Move them to a [global] section and pass them to cherrypy.config.update() instead of tree.mount().' % sn)
                warnings.warn(os.linesep.join(msg))

    def check_skipped_app_config(self):
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            if not app.config:
                msg = 'The Application mounted at %r has an empty config.' % sn
                if self.global_config_contained_paths:
                    msg += ' It looks like the config you passed to cherrypy.config.update() contains application-specific sections. You must explicitly pass application config via cherrypy.tree.mount(..., config=app_config)'
                warnings.warn(msg)
                return

    def check_app_config_brackets(self):
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            if not app.config:
                continue
            for key in app.config.keys():
                if key.startswith('[') or key.endswith(']'):
                    warnings.warn('The application mounted at %r has config section names with extraneous brackets: %r. Config *files* need brackets; config *dicts* (e.g. passed to tree.mount) do not.' % (sn, key))

    def check_static_paths(self):
        request = cherrypy.request
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            request.app = app
            for section in app.config:
                request.get_resource(section + '/dummy.html')
                conf = request.config.get
                if conf('tools.staticdir.on', False):
                    msg = ''
                    root = conf('tools.staticdir.root')
                    dir = conf('tools.staticdir.dir')
                    if dir is None:
                        msg = 'tools.staticdir.dir is not set.'
                    else:
                        fulldir = ''
                        if os.path.isabs(dir):
                            fulldir = dir
                            if root:
                                msg = 'dir is an absolute path, even though a root is provided.'
                                testdir = os.path.join(root, dir[1:])
                                if os.path.exists(testdir):
                                    msg += '\nIf you meant to serve the filesystem folder at %r, remove the leading slash from dir.' % testdir
                        elif not root:
                            msg = 'dir is a relative path and no root provided.'
                        else:
                            fulldir = os.path.join(root, dir)
                            if not os.path.isabs(fulldir):
                                msg = '%r is not an absolute path.' % fulldir
                        if fulldir and not os.path.exists(fulldir):
                            if msg:
                                msg += '\n'
                            msg += '%r (root + dir) is not an existing filesystem path.' % fulldir
                    if msg:
                        warnings.warn('%s\nsection: [%s]\nroot: %r\ndir: %r' % (msg,
                         section,
                         root,
                         dir))

    obsolete = {'server.default_content_type': 'tools.response_headers.headers',
     'log_access_file': 'log.access_file',
     'log_config_options': None,
     'log_file': 'log.error_file',
     'log_file_not_found': None,
     'log_request_headers': 'tools.log_headers.on',
     'log_to_screen': 'log.screen',
     'show_tracebacks': 'request.show_tracebacks',
     'throw_errors': 'request.throw_errors',
     'profiler.on': 'cherrypy.tree.mount(profiler.make_app(cherrypy.Application(Root())))'}
    deprecated = {}

    def _compat(self, config):
        for section, conf in config.items():
            if isinstance(conf, dict):
                for k, v in conf.items():
                    if k in self.obsolete:
                        warnings.warn('%r is obsolete. Use %r instead.\nsection: [%s]' % (k, self.obsolete[k], section))
                    elif k in self.deprecated:
                        warnings.warn('%r is deprecated. Use %r instead.\nsection: [%s]' % (k, self.deprecated[k], section))

            elif section in self.obsolete:
                warnings.warn('%r is obsolete. Use %r instead.' % (section, self.obsolete[section]))
            elif section in self.deprecated:
                warnings.warn('%r is deprecated. Use %r instead.' % (section, self.deprecated[section]))

    def check_compatibility(self):
        self._compat(cherrypy.config)
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            self._compat(app.config)

    extra_config_namespaces = []

    def _known_ns(self, app):
        ns = ['wsgi']
        ns.extend(copykeys(app.toolboxes))
        ns.extend(copykeys(app.namespaces))
        ns.extend(copykeys(app.request_class.namespaces))
        ns.extend(copykeys(cherrypy.config.namespaces))
        ns += self.extra_config_namespaces
        for section, conf in app.config.items():
            is_path_section = section.startswith('/')
            if is_path_section and isinstance(conf, dict):
                for k, v in conf.items():
                    atoms = k.split('.')
                    if len(atoms) > 1:
                        if atoms[0] not in ns:
                            if atoms[0] == 'cherrypy' and atoms[1] in ns:
                                msg = 'The config entry %r is invalid; try %r instead.\nsection: [%s]' % (k, '.'.join(atoms[1:]), section)
                            else:
                                msg = 'The config entry %r is invalid, because the %r config namespace is unknown.\nsection: [%s]' % (k, atoms[0], section)
                            warnings.warn(msg)
                        elif atoms[0] == 'tools':
                            if atoms[1] not in dir(cherrypy.tools):
                                msg = 'The config entry %r may be invalid, because the %r tool was not found.\nsection: [%s]' % (k, atoms[1], section)
                                warnings.warn(msg)

    def check_config_namespaces(self):
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            self._known_ns(app)

    known_config_types = {}

    def _populate_known_types(self):
        b = [ x for x in vars(builtins).values() if type(x) is type(str) ]

        def traverse(obj, namespace):
            for name in dir(obj):
                if name == 'body_params':
                    continue
                vtype = type(getattr(obj, name, None))
                if vtype in b:
                    self.known_config_types[namespace + '.' + name] = vtype

        traverse(cherrypy.request, 'request')
        traverse(cherrypy.response, 'response')
        traverse(cherrypy.server, 'server')
        traverse(cherrypy.engine, 'engine')
        traverse(cherrypy.log, 'log')

    def _known_types(self, config):
        msg = 'The config entry %r in section %r is of type %r, which does not match the expected type %r.'
        for section, conf in config.items():
            if isinstance(conf, dict):
                for k, v in conf.items():
                    if v is not None:
                        expected_type = self.known_config_types.get(k, None)
                        vtype = type(v)
                        if expected_type and vtype != expected_type:
                            warnings.warn(msg % (k,
                             section,
                             vtype.__name__,
                             expected_type.__name__))

            else:
                k, v = section, conf
                if v is not None:
                    expected_type = self.known_config_types.get(k, None)
                    vtype = type(v)
                    if expected_type and vtype != expected_type:
                        warnings.warn(msg % (k,
                         section,
                         vtype.__name__,
                         expected_type.__name__))

    def check_config_types(self):
        self._known_types(cherrypy.config)
        for sn, app in cherrypy.tree.apps.items():
            if not isinstance(app, cherrypy.Application):
                continue
            self._known_types(app.config)

    def check_localhost(self):
        for k, v in cherrypy.config.items():
            if k == 'server.socket_host' and v == 'localhost':
                warnings.warn("The use of 'localhost' as a socket host can cause problems on newer systems, since 'localhost' can map to either an IPv4 or an IPv6 address. You should use '127.0.0.1' or '[::1]' instead.")
