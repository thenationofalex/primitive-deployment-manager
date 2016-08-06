#!/usr/bin/env python3
'''Primitive Deployment Manager'''

import os
import json
import http.client
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

    print(colored('📡 🛰  Primitive Deployment Manager v0.0.1\n', 'magenta'))
    print(colored('Deploy \'' + deployment_data['codebase'][0]['name'] + '\' to:\n', 'cyan'))

    project_name = deployment_data['nodes'][0]['project_name']

    for nodes in deployment_data['nodes']:
        print('- ' + nodes['ip'])

    # Prepare package list
    packages = []
    for package in deployment_data['package']:
        packages.append(package['name'])

    packages_to_install = 'mkdir -p deploy/codebase/' + project_name + \
    ' && mkdir deploy/config && sudo -S apt-get install -y ' + ' '.join(packages)

    # Confirm codebase deployment to nodes.
    while True:
        confirm_deployment = input(colored('\nY or N: ', 'cyan')).lower()
        if confirm_deployment == 'n':
            print('Goodbye')
            raise SystemExit
        elif confirm_deployment == 'y':
            break
        else:
            print(colored('Y or N please', 'red'))

    # Start Paramiko Deployment
    for nodes in deployment_data['nodes']:
        print(colored('Connecting to: ' + nodes['ip'], 'cyan'))

        # Start SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(nodes['ip'], username=nodes['username'],
                    password=server_password, timeout=4)

        # Install Packages
        print(colored('Installing packages: ' + str(packages), 'cyan'))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(packages_to_install),
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())

        # Start SFTP
        transport = paramiko.Transport((nodes['ip'], 22))
        transport.connect(username=nodes['username'], password=server_password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Deploy configs
        print(colored('Copying configs:', 'cyan'))
        for config in deployment_data['config']:
            local_file = os.path.dirname(os.path.realpath(__file__)) + config['template']
            remote_file = '/home/' + nodes['username'] + config['template']
            print(local_file)
            sftp.put(local_file, remote_file)

        # Deploy code base
        print(colored('Copying codebase:', 'cyan'))
        for code in deployment_data['codebase']:
            local_folder = os.path.dirname(os.path.realpath(__file__)) + code['dir']
            remote_folder = '/home/' +  nodes['username'] + code['dir']
            for filename in os.listdir(local_folder):
                to_transfer = os.path.dirname(os.path.realpath(__file__)) + \
                code['dir'] + '/' + filename
                remote_transfer = remote_folder + '/' + filename
                print(to_transfer)
                sftp.put(to_transfer, remote_transfer)

        sftp.close()
        transport.close()

        # Move config files.
        for config in deployment_data['config']:
            configs_to_move = 'sudo -S cp -r /home/' + nodes['username'] + \
            config['template'] + ' ' + config['deploy_to']
            if config['service'] == 'webserver':
                site_to_enable = config['name']

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(configs_to_move),
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())

        # Set ServerName in Apache conf
        for config in deployment_data['config']:
            if config['service'] == 'webserver':
                update_server_name = 'sudo -S sed -i \'/.*ServerName.*/c\ServerName ' + \
                nodes['ip'] + '\' /etc/apache2/sites-available/helloworld.conf'

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(update_server_name),
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())

        # Move codebase
        for code in deployment_data['codebase']:
            code_to_move = 'sudo -S mkdir -p ' + code['deploy_to'] + \
            ' && sudo -S cp -r /home/' + nodes['username'] + '/' + code['dir'] + \
            '/* ' + code['deploy_to']

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(code_to_move),
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())

        # Clean up deployment directory, remove default apache site,
        # enable new site, restart apache services
        clean_up = 'sudo rm -rf /home/' + nodes['username'] + '/deploy && ' \
        'sudo -S rm -rf /var/www/html && sudo -S a2ensite ' + site_to_enable + \
        ' && sudo -S service restart apache2'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(clean_up),
                                                             get_pty=True)
        ssh_stdin.write(server_password + '\n')
        ssh_stdin.flush()
        print(ssh_stderr.read())
        print(ssh_stdout.read())

        ssh.close()

        #Run HTTP tests
        http_test = http.client.HTTPConnection(nodes['ip'])
        http_test.request("GET", "/")
        response = http_test.getresponse()
        data_response = response.read()
        print(colored('HTTP Test', 'cyan'))
        print(response.status, response.reason)
        print(data_response)

if __name__ == '__main__':
    main()
