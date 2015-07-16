#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    auto ssh
"""

import os
import json
from fabric.colors import *
from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.console import confirm

from common import *


jfile = open(env.inc).read()
jdata = json.loads(jfile)
print(jdata)

clusters = []
for i, h in jdata['kafka-pusher']['instance']:
    clusters.append(h['ip'])

print clusters

env.user = 'work'
env.hosts = clusters
env.hostnames = dict([h, '%d' % (i + 1)] for i, h in enumerate(devel_clusters))

env.relation = {
	'zookeeper' : (','.join(x + ':2181' for x in devel_clusters)),
}

pkgPath = '/home/work/deploy/packages'
cfgPath = '/home/work/deploy/config'


@task
def install(pid):
    dist = '/home/' + env.user + '/kafka-pusher-' + pid
    print green(dist)
    run('rm -rf ' + dist)
    run('mkdir -p ' + dist)
    put(pkgPath + '/kafka-pusher-0.1', dist)
    put(pkgPath + '/supervise', dist)
    with cd(dist):
        run('mkdir -p bin conf log data')
	run('mv kafka-pusher-0.1 bin/kafka-pusher')
	run('chmod 755 supervise bin/kakka-pusher')
    pass


@task
def config(pid):
    configDir = '/home/' + env.user + '/kafka-pusher-' + pid + '/conf'
    logDir = '/home/' + env.user + '/kafka-pusher-' + pid + '/logs'
    print green(configDir)




@task
def start(pid):
    dist = '/home/' + env.user + '/kafka-pusher-' + pid 
    with cd(dist):
	    run('bin/kafka-pusher -c conf/config.json &')


@task
def stop(pid):
    dist = '/home/' + env.user + '/kafka-pusher-' + pid 
    with cd(dist):
	    run('pkill kafka-pusher')

