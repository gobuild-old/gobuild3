# coding: utf-8
import sys
from ConfigParser import ConfigParser
from types import ModuleType

cfdefault = ConfigParser()
assert cfdefault.read('config.default.ini')

cf = ConfigParser()
cf.read('config.ini')

class GcfgSection(object):
    def __init__(self, default, user, section):
        self._section = section
        self._default = default
        self._user = user
    
    def __getattr__(self, name):
        value = self._default.get(self._section, name)
        try:
            value = self._user.get(self._section, name)
        except:
            pass
        return value


class SelfWrapper(ModuleType):
    def __init__(self, self_module, baked_args={}):
        for attr in ["__file__", "__hash__", "__buildins__", "__doc__", "__name__", "__package__"]:
            setattr(self, attr, getattr(self_module, attr, None))

        self.self_module = self_module

    def __getattr__(self, name):
        return GcfgSection(cfdefault, cf, name)

self = sys.modules[__name__]
sys.modules[__name__] = SelfWrapper(self)

