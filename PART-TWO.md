## 📡 🛰 Operations Challenge Part 2

![Author Alex Best](https://img.shields.io/badge/Author-Alex%20Best-red.svg?style=flat-square)

## Server: 54.197.4.164

### Problems Found

---

#### 1) Disk space full

```
Filesystem      Size  Used Avail Use% Mounted on
udev            815M   12K  815M   1% /dev
tmpfs           166M  208K  165M   1% /run
/dev/xvda1      9.9G  9.8G     0 100% /
none            4.0K     0  4.0K   0% /sys/fs/cgroup
none            5.0M     0  5.0M   0% /run/lock
none            826M     0  826M   0% /run/shm
none            100M     0  100M   0% /run/user
/dev/xvda2      147G   60M  140G   1% /mnt
```

##### Solution:

Tried to find large files using `du` and `lsof`.

`du` was unsuccessful.

`lsof` found one deleted resource that could be removed.

```
root@ip-172-31-255-101:~# lsof -nP | grep '(deleted)'
named      1433           root    3w      REG   202,1 9675644928      58025 /tmp/tmp.ekO7Q1I8Gu (deleted)
```

#####  Result

Freed 9098M through removal of stale tmp file.

```
root@ip-172-31-255-101:~# kill -9 1433
root@ip-172-31-255-101:~# df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            815M   12K  815M   1% /dev
tmpfs           166M  208K  165M   1% /run
/dev/xvda1      9.9G  802M  8.6G   9% /
```

---

#### 2) Could not resolve APT repositories

```
root@ip-172-31-255-101:~# view /etc/apt/sources.list
root@ip-172-31-255-101:~# apt-get update
Err http://security.ubuntu.com trusty-security InRelease

Err http://security.ubuntu.com trusty-security Release.gpg
  Could not resolve 'security.ubuntu.com'
Err http://us-east-1.ec2.archive.ubuntu.com trusty InRelease
...
```

`resolv.conf` Name server set to point to localhost

##### Solution

Set name server to Google public DNS `8.8.8.8` and added search `ap-us-east-1.compute.internal`
Restarted service

##### Result

APT updates and was able to install HTOP.

---

#### 3) P.D.M Deployed code base. HTTP response test failed.

Apache service not started and fails service restart

```
(98)Address already in use: AH00072: make_sock: could not bind to address 0.0.0.0:80
no listening sockets available, shutting down
AH00015: Unable to open logs
Action 'start' failed.
The Apache error log may have more information.
[fail]
```

Netstat shows port 80 bound to Netcat process

```
root@ip-172-31-255-101:/var/log# netstat -tulpn
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      1429/nc  
```

##### Solution

Killed process

##### Result

Lead to issue #4. Hello World still failed to respond.

---

#### 4) Port 80 still not open :(

Issue was caused by IPTables dropping connections for HTTP

```
root@ip-172-31-255-101:/etc# iptables -L --line-number
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    DROP       tcp  --  anywhere             anywhere             tcp dpt:http

....
```

#####  Solution

Removed DROP rule.

```
iptables -D INPUT 1
```

##### Result

Hello World is up :)
