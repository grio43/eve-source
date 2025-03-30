#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\reporting\report.py


class Report(object):

    def __init__(self, timestamp, key, attributes):
        self.timestamp = timestamp
        self.key = key
        self.attributes = attributes

    @staticmethod
    def from_dict(report_dict):
        for timestamp, report_data in report_dict.items():
            for key, attributes in report_data.items():
                return Report(timestamp, key, attributes)

    def to_dict(self):
        return {self.timestamp: {self.key: self.attributes}}


def report_to_yaml(dumper, report):
    return dumper.represent_dict(report.to_dict())


from yaml.representer import SafeRepresenter
SafeRepresenter.add_representer(Report, report_to_yaml)
