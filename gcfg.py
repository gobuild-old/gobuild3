# coding: utf-8
import sys
from ConfigParser import ConfigParser
from types import ModuleType
#import jenkins

cf = ConfigParser()
assert cf.read('config.ini')

class GcfgSection(object):
    def __init__(self, parser, section):
        self._section = section
        self._parser = parser
    
    def __getattr__(self, name):
        return self._parser.get(self._section, name)

class SelfWrapper(ModuleType):
    def __init__(self, self_module, baked_args={}):
        for attr in ["__file__", "__hash__", "__buildins__", "__doc__", "__name__", "__package__"]:
            setattr(self, attr, getattr(self_module, attr, None))

        self.self_module = self_module

    def __getattr__(self, name):
        return GcfgSection(cf, name)

self = sys.modules[__name__]
sys.modules[__name__] = SelfWrapper(self)


#JENKINS = jenkins.Jenkins(cf.get('jenkins', 'domain'), 
#        cf.get('jenkins', 'username'), cf.get('jenkins', 'password'))
