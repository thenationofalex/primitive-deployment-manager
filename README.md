## 📡 🛰  (P.D.M) Primitive Deployment Manager

![Author Alex Best](https://img.shields.io/badge/Author-Alex%20Best-red.svg?style=flat-square)
![Version 0.0.1](https://img.shields.io/badge/Version-0.0.1-orange.svg?style=flat-square)
![Python 3.5](https://img.shields.io/badge/Python%20-3.5-3776ab.svg?style=flat-square)

Primitive Deployment Manager is designed to quickly provision application servers.

### Built Using

- [Python 3.5](https://www.python.org)
- [Dotenv](https://github.com/theskumar/python-dotenv)
- [Paramiko](https://github.com/paramiko/paramiko)

### Application Structure

- **.env** Environment variables
- **src**
    - **primitive.py** The Application
    - **deply.json** Deployment configuration
    - **deploy** Deployment Assets
        - **config** System and App configs
        - **codebase**
            -**helloworld** Project to deploy

### Setup

- Install Python Dependencies via PIP `pip3 install -r requirements.txt`
- Rename `.env-sample` to `.env` and set server password.
- Define project configuration in `src/deploy.json`
    - **Nodes** List of nodes ***IP*** and ***USERNAME*** to that P.D.M will use deploy the application.
    - **Package** List of packages to install. (Currently only packages that can be install via APT)
    - **Codebase** Name and path to the application to deploy.
    - **Config** ...

Example config:

```
{
    "nodes": [
        {
            "ip": "192.168.1.149",
            "username": "alexb",
            "project_name": "helloworld"
        }
    ],
    "package": [
        {
            "name": "apache2"
        }
    ],
    "codebase": [
        {
            "name": "Hello World",
            "dir": "deploy/codebase/helloworld",
            "deploy_to": "/var/www/helloworld"
        }
    ],
    "config": [
        {
            "name": "php.ini",
            "template": "/deploy/config/php.ini",
            "deploy_to": "/etc/php5/apache2/",
            "service": "php"
        },
        {
            "name": "helloworld.conf",
            "template": "/deploy/config/helloworld.conf",
            "deploy_to": "/etc/apache2/sites-available/",
            "service": "apache2"
        }
    ]
}

```

### Usage

- Start via the command line `python3 src/primitive.py`
