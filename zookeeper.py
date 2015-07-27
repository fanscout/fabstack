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
pkgPath = './package'
cfgPath = './config'
port = '9092'


##
# load service instance, config & relation
##

jfile = open(env.inc).read()
jdata = json.loads(jfile)
print(jdata)
print jdata['kafka']['instance']

clusters = []
for ins in jdata['zookeeper']['instance']:
    clusters.append(ins['ip'])
    port = str(ins['port']['main'])

print green(clusters)

zk_addr = []
for ins in jdata['zookeeper']['instance']:
    zk_addr.append(ins['ip'] + ":" + str(ins['port']['main']))

print green(zk_addr)

zkAddr = (','.join(x for x in zk_addr))
zkPath = jdata['kafka']['config']['chroot']


##
# setup fabric env variables
##
env.user = 'work'
env.hosts = clusters
env.hostnames = dict([h, '%d' % (i + 1)] for i, h in enumerate(clusters))


print env.hostnames




##
# define standard callbacks
# void/install/config/start/stop/relation_change
##
@task
def void(pid):
    pass  

@task
def install(pid):
    dist = get_dist(pid)
    print green(dist)
    run('rm -rf ' + dist)
    run('mkdir -p ' + dist)
    put(pkgPath + '/zookeeper-3.4.6.tar.gz', dist)
    with cd(dist):
        run('tar zxvf zookeeper-3.4.6.tar.gz')
        run('mv zookeeper-3.4.6/{bin,conf,lib,src} . ')
        run('mv zookeeper-3.4.6/zookeeper-3.4.6.jar lib && rm -rf ' + dist + '/zookeeper-3.4.6*')
        run('mkdir data var log')
    pass

@task
def config(pid):
    dist = get_dist(pid)
    configDir = dist + '/conf'
    logDir = dist + 'log'
    print green(configDir)
    put(cfgPath + '/supervisor.conf', configDir)

    with cd(dist):
        run('cp conf/zoo_sample.cfg conf/zoo.cfg')
        run('echo "# cluster mode" >> conf/zoo.cfg')

        # cluster mode
        for h in env.hostnames:
            print red('echo "server.' + env.hostnames[h][:] + '=' + h + ':2888:3888" >> conf/zoo.cfg')
            run('echo "server.' + env.hostnames[h][:] + '=' + h + ':2888:3888" >> conf/zoo.cfg')

        # data/myid
        run('echo "' + env.hostnames[env.host_string] + '" > data/myid')

    # server.properties
    setProperty(configDir + '/zoo.cfg', 'dataDir=', dist + '/data')
    setProperty(configDir + '/zoo.cfg', 'clientPort=', port)

    # supervisord.conf
    content = """[program:zookeeper]
startsecs=2
autostart=true
autorestart=true
command=bin/zkServer.sh start 
"""
    with cd(dist):
        run('echo "%s" >> conf/supervisor.conf' % content)
        run('sed -i \'s/${OSP_ROOT}/%s/g\' conf/supervisor.conf' % dist.replace("/", "\\/"))
    #server config end


@task
def start(pid):
    dist = get_dist(pid)
    with cd(dist):
        run('supervisord -c conf/supervisor.conf')
        run('supervisorctl -c conf/supervisor.conf start all')

@task
def stop(pid):
    dist = get_dist(pid)
    with cd(dist):
        run('cat var/supervisord.pid | xargs kill -15')


def get_dist(pid):
    return '/home/work/zookeeper'
