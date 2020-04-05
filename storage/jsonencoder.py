import datetime
import json

data_type = "__data_type"
content = "__content"


class Encoder():
    def __init__(self, *args, **kwargs):
        self.custom = {Encoder:(lambda x:x, lambda x:x)}
        self.JSONEncoder.custom = self.custom
    def register(self, type_, encode, decode):
        self.custom.update({type_: (encode, decode)})

    def hook(self, dct):
        if data_type in dct:
            for ty in self.custom.keys():
                if str(ty) == dct[data_type]:
                    return self.custom[ty][1](dct[content])
            if dct[data_type] == "datetime.datetime":
                return datetime.datetime.fromisoformat(dct['iso'])
            elif dct[data_type] == "datetime.timedelta":
                return datetime.timedelta(seconds=dct['totalseconds'])
        return dct
    class JSONEncoder(json.JSONEncoder) :
        def default(self, obj):
            if isinstance(obj, tuple(self.custom.keys())):
                return {data_type: f'{type(obj)}', content: self.custom[type(obj)][0](obj)}
            if isinstance(obj, (datetime.datetime)):
                return {data_type: 'datetime.datetime', 'iso': obj.isoformat()}
            if isinstance(obj, (datetime.timedelta)):
                return {data_type: 'datetime.timedelta', 'totalseconds': obj.total_seconds()}
            return json.JSONEncoder.default(self, obj)
