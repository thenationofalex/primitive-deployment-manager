#!/usr/bin/env python3
'''Primitive Deployment Manager'''

import json
import subprocess

from termcolor import colored

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

PACKAGES_TO_INSTALL = 'sudo apt-get install -y ' + ' '.join(packages)

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

# Start deployment
for nodes in DEPLOYMENT_DATA['nodes']:
    print(colored('Connecting to: ' + nodes['ip'] + '\n', 'cyan'))
    ssh = subprocess.Popen(['ssh', nodes['username'] + '@' + nodes['ip'], PACKAGES_TO_INSTALL],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE
                          )
    results = ssh.stdout.readlines()
    if results == []:
        error = ssh.stderr.readlines()
        print(error)
    else:
        print(results)
        # Connect to node X
            #Install Apache
            #Install PHP
            #Update PHP.INI
            #Setup Apache conf
            #Remove index.html
            #Deploy codebase
