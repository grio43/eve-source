#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\metrics.py
import time
from numbers import Number
from datadog.api.exceptions import ApiError
from datadog.api.resources import SearchableAPIResource, SendableAPIResource

class Metric(SearchableAPIResource, SendableAPIResource):
    _class_url = None
    _json_name = 'series'
    _METRIC_QUERY_ENDPOINT = '/query'
    _METRIC_SUBMIT_ENDPOINT = '/series'

    @classmethod
    def _process_points(cls, points):
        return cls._format_points(points if isinstance(points, list) else [points], time.time())

    @classmethod
    def _format_points(cls, points_lst, now):
        formatted_points = []
        while points_lst:
            try:
                if not points_lst:
                    return []
                point = points_lst.pop()
                timestamp = now if isinstance(point, Number) else point[0]
                value = float(point) if isinstance(point, Number) else float(point[1])
                point = (timestamp, value)
                formatted_points.append(point)
            except TypeError as e:
                raise TypeError(u'{0}: `points` parameter must use real numerical values.'.format(e))
            except IndexError as e:
                raise IndexError(u'{0}: `points` must be a list of values or a list of (timestamp, value) pairs'.format(e))

        return formatted_points

    @classmethod
    def send(cls, metrics = None, **single_metric):

        def rename_metric_type(metric):
            if 'metric_type' in metric:
                metric['type'] = metric.pop('metric_type')

        cls._class_url = cls._METRIC_SUBMIT_ENDPOINT
        try:
            if metrics:
                for metric in metrics:
                    if isinstance(metric, dict):
                        rename_metric_type(metric)
                        metric['points'] = cls._process_points(metric['points'])

                metrics_dict = {'series': metrics}
            else:
                rename_metric_type(single_metric)
                single_metric['points'] = cls._process_points(single_metric['points'])
                metrics = [single_metric]
                metrics_dict = {'series': metrics}
        except KeyError:
            raise KeyError("'points' parameter is required")

        return super(Metric, cls).send(attach_host_name=True, **metrics_dict)

    @classmethod
    def query(cls, **params):
        cls._class_url = cls._METRIC_QUERY_ENDPOINT
        try:
            params['from'] = params.pop('start')
            params['to'] = params.pop('end')
        except KeyError as e:
            raise ApiError("The parameter '{0}' is required".format(e.args[0]))

        return super(Metric, cls)._search(**params)
