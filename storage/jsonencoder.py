import datetime
import json


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime)):
            return {'data_type':'datetime.datetime', 'iso':obj.isoformat()}
        if isinstance(obj, (datetime.timedelta)):
            return {'data_type':'datetime.timedelta', 'totalseconds':obj.total_seconds()}
        return json.JSONEncoder.default(self, obj)


def hook(dct):
    if 'data_type' in dct:
        if dct['data_type'] == "datetime.datetime":
            return datetime.datetime.fromisoformat(dct['iso'])
        elif dct['data_type'] == "datetime.timedelta":
            return datetime.timedelta(seconds=dct['totalseconds'])
    return dct
