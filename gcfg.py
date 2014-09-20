# coding: utf-8
from ConfigParser import ConfigParser
import jenkins

cf = ConfigParser()
assert cf.read('config.ini')

JENKINS = jenkins.Jenkins(cf.get('jenkins', 'domain'), 
        cf.get('jenkins', 'username'), cf.get('jenkins', 'password'))
