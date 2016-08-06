#!/usr/bin/env python3
'''Primitive Deployment Manager'''

import os
import json
import paramiko

from dotenv  import Dotenv
from termcolor import colored

DOTENV_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../.env'
DOTENV = Dotenv(DOTENV_PATH)
os.environ.update(DOTENV)

# Load deployment config,
DEPLOYMENT_DATA = []
with open('src/deploy.json') as deployment_config:
    DEPLOYMENT_DATA = json.load(deployment_config)

print(colored('\n📡 🛰  Primitive Deployment Manager v0.0.1\n', 'magenta'))
print(colored('Deploy \'' + DEPLOYMENT_DATA['codebase'][0]['name'] + '\' to: (Y/N)\n', 'cyan'))

for nodes in DEPLOYMENT_DATA['nodes']:
    print('- ' + nodes['ip'])

# Prepare package list
packages = []
for package in DEPLOYMENT_DATA['package']:
    packages.append(package['name'])

PACKAGES_TO_INSTALL = 'sudo -S apt-get install -y ' + ' '.join(packages)

# Confirm codebase deployment to nodes.
while True:
    CONFIRM_DEPLOYMENT = input('\n')
    CONFIRM_DEPLOYMENT = CONFIRM_DEPLOYMENT.lower()
    if CONFIRM_DEPLOYMENT == 'n':
        print('Goodbye')
        raise SystemExit
    elif CONFIRM_DEPLOYMENT == 'y':
        break
    else:
        print(colored('Y or N please', 'red'))

# Start Paramiko Deployment
cmd_to_execute = str(PACKAGES_TO_INSTALL)
for nodes in DEPLOYMENT_DATA['nodes']:
    print(colored('Connecting to: ' + nodes['ip'], 'cyan'))
    SSH = paramiko.SSHClient()
    SSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH.connect(nodes['ip'], username=nodes['username'], password=os.environ.get('SERVER_PASSWORD'))
    print('Installing packages ' + str(packages))
    ssh_stdin, ssh_stdout, ssh_stderr = SSH.exec_command(cmd_to_execute, get_pty=True)
    ssh_stdin.write(os.environ.get('SERVER_PASSWORD') + '\n')
    ssh_stdin.flush()
    print(ssh_stdout.read())
    SSH.close()

    # outlines = ssh_stdout.readlines()
    # errlines = ssh_stderr.readlines()
    # resp=''.join(outlines)
    # resp=''.join(errlines)
    # print(resp)
    # SSH.close()

# Start deployment
# for nodes in DEPLOYMENT_DATA['nodes']:
#     print(colored('Connecting to: ' + nodes['ip'] + '\n', 'cyan'))
#     ssh = subprocess.Popen(['ssh', nodes['username'] + '@' + nodes['ip'], PACKAGES_TO_INSTALL],
#                            shell=False,
#                            stdout=subprocess.PIPE,
#                            stderr=subprocess.PIPE
#                           )
#     results = ssh.stdout.readlines()
#     if results == []:
#         error = ssh.stderr.readlines()
#         print(error)
#     else:
#         print(results)
        # Connect to node X
            #Install Apache
            #Install PHP
            #Update PHP.INI
            #Setup Apache conf
            #Remove index.html
            #Deploy codebase
