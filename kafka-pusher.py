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

devel_clusters = ['10.0.20.32', '10.0.20.33', '10.0.20.34']


#jfile = open(include).read()
#jdata = json.loads(jfile)

print(env.foo)



env.user = 'work'
env.hosts = devel_clusters
env.hostnames = dict([h, '%d' % (i + 1)] for i, h in enumerate(devel_clusters))
env.roledefs = {
	'zookeeper' : devel_clusters
}

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
    configDir = '/home/' + env.user + '/kafka-' + pid + '/config'
    logDir = '/home/' + env.user + '/kafka-' + pid + '/logs'
    print green(configDir)
    put(cfgPath + '/kafka_server_properties', configDir + '/server.properties')

    # server.properties
    setProperty(configDir + '/server.properties', 'broker.id=', env.hostnames[env.host_string][:])
    setProperty(configDir + '/server.properties', 'log.dirs=', logDir)
    setProperty(configDir + '/server.properties', 'zookeeper.connect=', env.relation['zookeeper'] + '/kafka/' + pid)


@task
def start(pid):
    dist = '/home/' + env.user + '/kafka-' + pid 
    with cd(dist):
	run('bin/kafka-server-start.sh -daemon config/server.properties')


@task
def stop(pid):
    dist = '/home/' + env.user + '/kafka-' + pid 
    with cd(dist):
	run('bin/kafka-server-stop.sh')

