#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    auto ssh
"""

import os
from fabric.colors import *
from fabric.api import *
from fabric.context_managers import *

def setProperty(fname, prop, value):
    with settings(warn_only=True):
        result = run("grep -n '%s' %s | awk -F: '{print $1}'" % (prop, fname))
    if result == '':
        run("sed -i '$i %s' %s" % (prop + value, fname))
    else:
        num = int(result)
        run("sed -i '%dc %s' %s" % (num, prop + value, fname))

def puttar(fname):
    print yellow('start to put %s' % fname)
    with cd("/tmp"):
        if run('ls').find(fname) == -1:
            with settings(warn_only=True):
                result = put("./tars/%s" % fname, "/tmp/%s" % fname)
            if result.failed and not confirm("put tar file failed, Continue[Y/N]"):
                abort("Aborting file put tar task!")
        else:
            print yellow('%s already exists! ' % fname)


def checkmd5(fname):
    with settings(warn_only=True):
        lmd5 = local("md5sum ./tars/" + fname, capture=True).split(' ')[0]
        rmd5 = run("md5sum /tmp/" + fname).split(' ')[0]
    if lmd5 == rmd5:
        print green("Successfully put " + fname + " !")
    else:
        print red("failed to put " + fname + " !")


def untarfile(key, fname):
    with cd("/tmp"):
        dirname = run("tar tf " + fname + " | head -n 1 | awk -F / '{{print $1}}'")
        with cd(optDir):
            sudo("rm -rf " + dirname)
        with settings(warn_only=True):
            sudo("tar -xzf %s -C %s" % (fname, optDir))
        with cd(optDir):
            sudo('chown -R %s:%s %s' % (newuser, newgroup, dirname))
    with cd("/usr/local"):
        sudo("rm -rf " + key)
        sudo("ln -s %s/%s %s" % (optDir, dirname, key))


def processTar(key, fname):
    puttar(fname)
    checkmd5(fname)
    untarfile(key, fname)



