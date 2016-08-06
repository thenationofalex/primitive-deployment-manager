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

    # Prepare package list
def prepare_packages(deployment_data, project_name):
    '''Create list of APT packages to install'''
    packages = []
    for package in deployment_data['package']:
        packages.append(package['name'])
    packages_to_install = 'mkdir -p deploy/codebase/' + project_name + \
    ' && mkdir deploy/config && sudo -S apt-get install -y ' + ' '.join(packages)
    return packages_to_install

def install_packages(ssh, packages_to_install, password):
    '''Install packages via APT'''
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(packages_to_install),
                                                         get_pty=True)
    ssh_stdin.write(password + '\n')
    ssh_stdin.flush()
    ssh_stderr.read()
    ssh_stdout.read()

def deploy_config(sftp, deployment_data, username):
    '''SFTP Config files'''
    for config in deployment_data['config']:
        local_file = os.path.dirname(os.path.realpath(__file__)) + config['template']
        remote_file = '/home/' + username + config['template']
        print(local_file)
        sftp.put(local_file, remote_file)

def deploy_code_base(sftp, deployment_data, username):
    '''SFTP Codebase'''
    for code in deployment_data['codebase']:
        local_folder = os.path.dirname(os.path.realpath(__file__)) + code['dir']
        remote_folder = '/home/' +  username + code['dir']
        for filename in os.listdir(local_folder):
            to_transfer = os.path.dirname(os.path.realpath(__file__)) + \
            code['dir'] + '/' + filename
            remote_transfer = remote_folder + '/' + filename
            print(to_transfer)
            sftp.put(to_transfer, remote_transfer)

def move_config_files(ssh, deployment_data, username, password):
    '''Move config files and return site name'''
    for config in deployment_data['config']:
        configs_to_move = 'sudo -S cp -r /home/' + username + \
        config['template'] + ' ' + config['deploy_to']

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(configs_to_move),
                                                         get_pty=True)
    ssh_stdin.write(password + '\n')
    ssh_stdin.flush()
    ssh_stderr.read()
    ssh_stdout.read()

def set_servername(ssh, deployment_data, ip_address, password):
    '''Set ServerName in Apache VirtualHost'''
    for config in deployment_data['config']:
        if config['service'] == 'webserver':
            update_server_name = 'sudo -S sed -i \'/.*ServerName.*/c\\ServerName ' + \
            ip_address + '\' /etc/apache2/sites-available/helloworld.conf'

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(update_server_name),
                                                         get_pty=True)
    ssh_stdin.write(password + '\n')
    ssh_stdin.flush()
    ssh_stderr.read()
    ssh_stdout.read()

def move_code_base(ssh, deployment_data, username, password):
    '''Move Codebase'''
    for code in deployment_data['codebase']:
        code_to_move = 'sudo -S mkdir -p ' + code['deploy_to'] + \
        ' && sudo -S cp -r /home/' + username + '/' + code['dir'] + \
        '/* ' + code['deploy_to']

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(code_to_move),
                                                         get_pty=True)
    ssh_stdin.write(password + '\n')
    ssh_stdin.flush()
    ssh_stderr.read()
    ssh_stdout.read()

def clean_up_deployment(ssh, username, site, password):
    '''Clean up deployment directory, remove default apache site,
    enable new site, restart apache services'''
    clean_up = 'sudo rm -rf /home/' + username + '/deploy && ' \
    'sudo -S rm -rf /var/www/html && sudo -S a2ensite ' + site + \
    ' && sudo -S service apache2 restart'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str(clean_up),
                                                         get_pty=True)
    ssh_stdin.write(password + '\n')
    ssh_stdin.flush()
    ssh_stderr.read()
    ssh_stdout.read()

def run_http_test(ip_address):
    '''Test server http response'''
    http_test = http.client.HTTPConnection(ip_address)
    http_test.request("GET", "/")
    response = http_test.getresponse()
    data_response = response.read()
    print(colored('HTTP Test', 'cyan'))
    print(response.status, response.reason)
    print(data_response)

def main():
    '''Start Primitive Deployment Manager'''
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
        packages_to_install = prepare_packages(deployment_data, project_name)
        print(colored('Installing packages', 'cyan'))
        install_packages(ssh, packages_to_install, server_password)

        # Start SFTP
        transport = paramiko.Transport((nodes['ip'], 22))
        transport.connect(username=nodes['username'], password=server_password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Deploy configs
        print(colored('Copying configs:', 'cyan'))
        deploy_config(sftp, deployment_data, nodes['username'])

        # Deploy code base
        print(colored('Copying codebase:', 'cyan'))
        deploy_code_base(sftp, deployment_data, nodes['username'])

        sftp.close()
        transport.close()

        # Move config files.
        move_config_files(ssh, deployment_data, nodes['username'], server_password)

        # Set ServerName in Apache conf
        set_servername(ssh, deployment_data, nodes['ip'], server_password)

        # Move codebase
        move_code_base(ssh, deployment_data, nodes['username'], server_password)

        # Clean up deployment directory, remove default apache site,
        # enable new site, restart apache services
        for config in deployment_data['config']:
            if config['service'] == 'webserver':
                site_to_enable = config['name']
        clean_up_deployment(ssh, nodes['username'], site_to_enable, server_password)

        ssh.close()

        #Run HTTP tests
        run_http_test(nodes['ip'])
        print(colored('Node deployed', 'magenta'))

if __name__ == '__main__':
    main()
