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
for i, h in jdata['kafka-proxy']['instance']:
    clusters.append(h['ip'])

print clusters

zkAddr = []
for i, h in  jdata['zookeeper']['instance']:
    zk_addr.append(h['ip'] + ":" + h['port']['main'])

zkPath = jdata['kafka']['config']['chroot']

print green(zkAddr)
print green(zkPath)

env.user = 'work'
env.hosts = clusters
env.hostnames = dict([h, '%d' % (i + 1)] for i, h in enumerate(devel_clusters))


pkgPath = '/home/work/deploy/packages'
cfgPath = '/home/work/deploy/config'


@task
def install(pid):
    dist = '/home/' + env.user + '/kafka-proxy-' + pid
    print green(dist)
    run('rm -rf ' + dist)
    run('mkdir -p ' + dist)
    put(pkgPath + '/kafka-proxy-0.1', dist)
    put(pkgPath + '/supervise', dist)
    with cd(dist):
        run('mkdir -p bin conf log data')
	run('mv kafka-proxy-0.1 bin/kafka-proxy')
	run('chmod 755 supervise bin/kakka-proxy')
    pass


@task
def config(pid):
    configDir = '/home/' + env.user + '/kafka-proxy-' + pid + '/conf'
    logDir = '/home/' + env.user + '/kafka-proxy-' + pid + '/logs'
    print green(configDir)
    put(cfgPath + '/kafka_proxy_cfg', configDir + '/proxy.cfg')
    setProperty(configDir + '/proxy.cfg', 'port=', port)
    setProperty(configDir + '/proxy.cfg', 'addr=', port)


@task
def start(pid):
    dist = '/home/' + env.user + '/kafka-proxy-' + pid 
    with cd(dist):
	    run('bin/kafka-proxy -c conf/config.json &')


@task
def stop(pid):
    dist = '/home/' + env.user + '/kafka-proxy-' + pid 
    with cd(dist):
	    run('pkill kafka-proxy')

