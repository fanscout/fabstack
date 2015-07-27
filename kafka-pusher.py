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
print jdata

clusters = []
for ins in jdata['kafka-pusher']['instance']:
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


##
# define standard callbacks
# void/install/config/start/stop/relation_change
##
@task
def void(pid):
    print green(get_dist(pid))
    pass  

@task
def install(pid):
    dist = get_dist(pid)
    print green(dist)
    run('rm -rf ' + dist)
    run('mkdir -p ' + dist)
    put(pkgPath + '/kafka-pusher-0.1', dist)
    put(pkgPath + '/supervise', dist)
    with cd(dist):
        run('mkdir -p bin conf log data var')
        run('mv kafka-pusher-0.1 bin/kafkapusher')
        run('chmod 755 supervise bin/kafkapusher')
    pass

@task
def config(pid):
    dist = get_dist(pid)
    configDir = dist + '/conf'
    put(cfgPath + '/supervisord.conf', configDir)
    with cd(dist):
        content = """
[program:kafkapusher]
startsecs=2
autostart=true
autorestart=true
command=bin/kafkapusher -c conf/config.json -log_dir=log
"""
        run('echo "%s" >> conf/supervisord.conf' % content)
        run('sed -i "s/work/%s/g" conf/supervisord.conf' % dist.replace("/", "\\\\/"))
    # server.properties

@task
def start(pid):
    dist = get_dist(pid)
    with cd(dist):
        run('supervisord -c conf/supervisor.conf')
        run('supervisorctl -c conf/supervisord.conf start all')

@task
def stop(pid):
    dist = get_dist(pid)
    with cd(dist):
        run('cat var/supervisord.pid | xargs kill -15')


#####
def get_dist(pid):
    dist = '/home/' + env.user + '/kafkapusher-' + pid
    return dist


