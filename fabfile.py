#!/bin/env python


from fabric.api import *
from fabric.state import *
from optparse import OptionParser
import ConfigParser as configparser
import os

parser = OptionParser()
parser.add_option("-c", "--config", dest="config", help="write report to CONFIG", metavar="CONFIG")
parser.add_option("-p", "--process", dest="process", help="process to execute", metavar="PROCESS")
parser.add_option("-u", "--user", dest="user",help="user to execute command", metavar="USER")
(options,args) = parser.parse_args()

file_exists = False
process_config = None
hosts = None
current_task = None
proces = None
valid_process = False
execute_script = False
script = None

if os.path.isfile(options.config):
    file_exists = True

if file_exists:
    process_config = configparser.ConfigParser()
    process_config.read(options.config)

if process_config is not None:
    if process_config.has_section(options.process):
        process = options.process
        if process_config.has_option(options.process,"hosts"):
            hosts = process_config.get(options.process,"hosts")
        if process_config.has_option(options.process,"task"):
            current_task = r'%s' % process_config.get(options.process,"task")
        if process_config.has_option(options.process,"script"):
            execute_script = True
            script = process_config.get(options.process,"script")

    else:
        print "No configuration for the process %s." % options.process


if process is not None and hosts is not None and (current_task is not None or execute_script):
    valid_process = True

#env.parallel = True
env.user = options.user
#env.password = ''
#env.hosts = ['localhost','nitro']
env.hosts = hosts.split(",")
env.warn_only = True

"""
env.roledefs = {
    'remote':{
        'hosts': ["remote1","remote2"],
        'foo':'bar'
    },
    'local':{
        'hosts': ["localhost1","localhost2"],
        'foo':'buzz'
    }
}
"""
def host_type():
    try:
        if valid_process:
            if current_task is not None:
                tasks = current_task.split(",")
                for t in tasks:
                    ret = run(t.replace("\"",""))
                    cmd_exit_code = ret.return_code
                    if cmd_exit_code != 0:
                        print "Execution failed for '%s' with exit code: %s." % (t,cmd_exit_code)
            if execute_script:
                run('mkdir -p /tmp/testing')
                put('tests','/tmp/testing')
                ret = run("sh /tmp/testing/%s" % script)
                if ret.return_code != 0:
                    print "Script execution %s failed." % script
                else:
                    run('rm -rf /tmp/testing')
    except Exception,e:
        print "Encountered an error while executing host_type"
        e = str(e)
        print "Here is the error: %s" %e
