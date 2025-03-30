#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\ajaxwriter.py
import json
from carbon.common.script.util import htmlwriter
from carbon.common.script.util.format import EscapeSQL

class AjaxWriter(htmlwriter.HtmlWriter):
    __dependencies__ = []

    def __init__(self, ajaxfilter, neededRoles, session):
        htmlwriter.HtmlWriter.__init__(self, template='script:/wwwroot/lib/template/empty.html')
        self.ajaxfilter = ajaxfilter
        self.neededRoles = neededRoles
        self.session = session
        try:
            self.DB2 = sm.services['DB2']
        except:
            pass

    def WriteJsonGridList(self, columns, data, pageNumber, numberOfPages):
        colFunc = lambda row: '{"id":"%(id)s","cell":%(cell)s}' % {'id': unicode(getattr(row, columns[0], None)()),
         'cell': unicode([ unicode(getattr(row, c1, None)()) for c1 in columns ]).replace("'", '"')}
        self.Write('{"page":"%(page)s","total":%(total)s,"records":"%(records)s","rows":[%(rows)s]}' % {'page': str(pageNumber),
         'total': str(numberOfPages),
         'records': str(len(data)),
         'rows': str(','.join(map(colFunc, data)))})

    def WriteJsonList(self, valueId, captionId, data):
        buff = []
        for row in data:
            val = getattr(row, valueId, None)
            if hasattr(val, '__call__'):
                val = val()
            label = getattr(row, captionId, None)
            if hasattr(label, '__call__'):
                label = label()
            buff.append({'id': val,
             'label': label})

        self.Write(json.dumps(buff, separators=(',', ':')))

    def ToJson(self, kpart, labelpart):
        return json.dumps({'id': kpart,
         'label': labelpart})

    def HasAccess(self):
        return session.userid and session.role & self.neededRoles

    def Lookup(self, table, key_field, value_field):
        if not self.HasAccess:
            return self.Write('[]')
        rs = self.DB2.GetSchema('zsystem').Lookup(table, key_field, value_field, None, None, None, EscapeSQL(unicode(self.ajaxfilter)), 0)
        return self.WriteJsonList(key_field, value_field, rs)

    def MediaTypeBin(self):
        self.response.contentType = 'application/octet-stream'

    def MediaTypeJson(self):
        self.response.contentType = 'application/json; charset=utf-8'

    def MediaTypeXml(self):
        self.response.contentType = 'application/xhtml+xml'

    def MediaTypeAtom(self):
        self.response.contentType = 'application/atom+xml'

    def HandleAction(self, action, request, response):
        self.request = request
        self.response = response
        argstuple = self.GetActionArgs(request, action)
        if argstuple:
            args, kwargs = argstuple
            try:
                getattr(self, action)(*args, **kwargs)
            except TypeError as e:
                sm.services['http'].LogError('Bad params (', kwargs, ') sent to ', action, ', resulting in exception: ', e)
                raise

        else:
            self.Write('[]')
