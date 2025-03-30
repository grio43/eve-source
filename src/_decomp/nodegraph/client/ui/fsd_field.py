#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\ui\fsd_field.py
import localization
from eveui.autocomplete import AutocompleteField, Suggestion, fuzzy_match

class DataSuggestion(Suggestion):
    __slots__ = ('data_id',)
    key_attributes = __slots__

    def __init__(self, data_id):
        self.data_id = data_id

    @property
    def text(self):
        return str(self.data_id)

    @property
    def subtext(self):
        return u'id:{}'.format(self.data_id)


class DataField(AutocompleteField):

    def __init__(self, get_data, get_data_name, data_id = None, **kwargs):
        self.get_data = get_data
        self.get_data_name = get_data_name
        if data_id is not None:
            kwargs['completed_suggestion'] = DataSuggestion(data_id=data_id)
        kwargs['provider'] = self.fetch_suggestions
        kwargs.setdefault('suggestion_list_min_width', 360)
        super(DataField, self).__init__(get_suggestion_text=self._get_suggestion_text, **kwargs)

    def get_value(self):
        if not self.completed_suggestion:
            return None
        return self.completed_suggestion.data_id

    def _get_suggestion_text(self, suggestion):
        return self._get_data_name(suggestion.data_id)

    def _get_data_name(self, data_id):
        if data_id is None:
            return ''
        name = self.get_data_name(data_id)
        if not name:
            return unicode(data_id)
        if isinstance(name, int):
            name = localization.GetByMessageID(name)
        return name

    def fetch_suggestions(self, query, previous_suggestions):
        try:
            int_query = int(query)
        except ValueError:
            int_query = None

        if int_query:
            for data_id in self.get_data():
                str_data_id = str(data_id)
                if query in str_data_id:
                    suggestion = DataSuggestion(data_id=data_id)
                    if int_query == data_id:
                        score = 1
                    elif str_data_id.startswith(query):
                        score = 0.9
                    else:
                        score = int_query - data_id
                    yield (score, suggestion)

        else:
            for data_id in self.get_data():
                suggestion = DataSuggestion(data_id=data_id)
                match, score, _ = fuzzy_match(query, self._get_data_name(data_id))
                if match:
                    yield (score, suggestion)


class FsdLoaderField(DataField):

    def __init__(self, fsd_loader = None, name_param = None, **kwargs):
        self.name_param = name_param or 'name'
        super(FsdLoaderField, self).__init__(get_data=fsd_loader().GetData, get_data_name=self._get_data_name, **kwargs)

    def _get_data_name(self, data_id):
        fsd_object = self.get_data().get(data_id, {})
        name = getattr(fsd_object, self.name_param, getattr(fsd_object, 'nameID', ''))
        if isinstance(name, int):
            name = localization.GetByMessageID(name)
        if name:
            return u'{} ({})'.format(name, data_id)
        return u'{}'.format(data_id)


class KeyValueFsdLoaderField(DataField):

    def __init__(self, fsd_loader = None, **kwargs):
        super(KeyValueFsdLoaderField, self).__init__(get_data=fsd_loader().GetData, get_data_name=self._get_data_name, **kwargs)

    def _get_data_name(self, data_id):
        value = self.get_data().get(data_id, {})
        if isinstance(value, int):
            value = localization.GetByMessageID(value)
        return value
