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


##
# local configs
##
pkgPath = '/home/work/deploy/packages'
cfgPath = '/home/work/deploy/config'
port = '9092'


##
# load service instance, config & relation
##

jfile = open(env.inc).read()
jdata = json.loads(jfile)
print jdata

clusters = []
for ins in jdata['kafka-proxy']['instance']:
    clusters.append(ins['ip'])
    port = str(ins['port']['main'])

print green(clusters)

zk_addr = []
for ins in jdata['zookeeper']['instance']:
    zk_addr.append(ins['ip'] + ":" + str(ins['port']['main'])))))

print green(zk_addr)

zkAddr = (','.join(x for x in zk_addr))
zkPath = jdata['kafka']['config']['chroot']


##
# setup fabric env variables
##
env.user = 'work'
env.hosts = clusters
env.hostnames = dict([h, '%d' % (i + 1)] for i, h in enumerate(clusters))


##
# define standard callbacks
# void/install/config/start/stop/relation_change
##
@task
def void(pid):
    pass  

@task
def install(pid):
    dist = '/home/' + env.user + '/kafkaproxy-' + pid
    print green(dist)
    run('rm -rf ' + dist)
    run('mkdir -p ' + dist)
    put(pkgPath + '/kafka-proxy-0.1', dist)
    put(pkgPath + '/supervise', dist)
    with cd(dist):
        run('mkdir -p bin conf log data supervise.d')
        run('mv kafka-proxy-0.1 bin/kafka-pusher')
        run('chmod 755 supervise bin/kakka-pusher')
    pass

@task
def config(pid):
    configDir = '/home/' + env.user + '/kafkaproxy-' + pid + '/conf'
    logDir = '/home/' + env.user + '/kafkaproxy-' + pid + '/log'
    print green(configDir)
    put(cfgPath + '/kafkaproxy_cfg', configDir + '/proxy.cfg')
    
    # proxy.cfg
    setProperty(configDir + '/proxy.cfg', 'port=', port)
    setProperty(configDir + '/proxy.cfg', 'addr=', zkAddr + zkPath + "/" + pid)

@task
def start(pid):
    dist = '/home/' + env.user + '/kafkaproxy-' + pid 
    with cd(dist):
	    run('./supervise supervise.d')

@task
def stop(pid):
    dist = '/home/' + env.user + '/kafkaproxy-' + pid 
    with cd(dist):
	    run('bin/kafka-server-stop.sh')

