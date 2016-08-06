#!/usr/bin/env python3
'''Primitive Deployment Manager'''

import os
import json
import paramiko

from dotenv  import Dotenv
from termcolor import colored

paramiko.util.log_to_file(os.path.dirname(os.path.realpath(__file__)) + '/../paramiko.log')
DOTENV_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../.env'
DOTENV = Dotenv(DOTENV_PATH)
os.environ.update(DOTENV)

def main():
    '''Main'''
    # Load deployment config
    server_password = os.environ.get('SERVER_PASSWORD')
    deployment_data = []
    with open('src/deploy.json') as deployment_config:
        deployment_data = json.load(deployment_config)

    print(colored('\n📡 🛰  Primitive Deployment Manager v0.0.1\n', 'magenta'))
    print(colored('Deploy \'' + deployment_data['codebase'][0]['name'] + '\' to: (Y/N)\n', 'cyan'))

    for nodes in deployment_data['nodes']:
        print('- ' + nodes['ip'])

    # Prepare package list
    packages = []
    for package in deployment_data['package']:
        packages.append(package['name'])

    packages_to_install = 'mkdir -p deploy/codebase && mkdir deploy/config \
    && sudo -S apt-get install -y ' + ' '.join(packages)

    # Confirm codebase deployment to nodes.
    while True:
        confirm_deployment = input('\n').lower()
        if confirm_deployment == 'n':
            print('Goodbye')
            raise SystemExit
        elif confirm_deployment == 'y':
            break
        else:
            print(colored('Y or N please', 'red'))

    # Start Paramiko Deployment
    cmd_to_execute = str(packages_to_install)
    for nodes in deployment_data['nodes']:
        print(colored('Connecting to: ' + nodes['ip'], 'cyan'))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(nodes['ip'], username=nodes['username'],
                    password=server_password, timeout=4)

        # Install Packages
        print('Installing packages ' + str(packages))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute,
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())
        ssh.close()

        # Copy configs over to remote deployment directory
        transport = paramiko.Transport((nodes['ip'], 22))
        transport.connect(username=nodes['username'], password=server_password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        print('Copying configs')
        for config in deployment_data['config']:
            local_file = os.path.dirname(os.path.realpath(__file__)) + config['template']
            remote_file = '/home/' +  nodes['username'] + config['template']
            sftp.put(local_file, remote_file)

        # Deploy code base
        print('Copying codebase')
        for code in deployment_data['codebase']:
            local_folder = os.path.dirname(os.path.realpath(__file__)) + code['dir']
            remote_folder = '/home/' +  nodes['username'] + code['dir']
            sftp.put(local_folder, remote_folder)
        sftp.close()

        # Remove index.html

        # Restart services

        # Run CURL tests

if __name__ == '__main__':
    main()
