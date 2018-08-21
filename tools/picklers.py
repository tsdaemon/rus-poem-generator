import pickle

from pymorphy2 import MorphAnalyzer
from russtress import Accent


class PosPickler(pickle.Pickler):
    def persistent_id(self, obj):
        if isinstance(obj, MorphAnalyzer):
            return "pymorphy2.MorphAnalyzer"
        elif isinstance(obj, Accent):
            return "russtress.Accent"
        else:
            return None


class PosUnpickler(pickle.Unpickler):
    def __init__(self, file):
        super().__init__(file)

    def persistent_load(self, id):
        if id == "pymorphy2.MorphAnalyzer":
            return MorphAnalyzer()
        elif id == "russtress.Accent":
            return Accent()
        else:
            raise pickle.UnpicklingError("unsupported persistent object")