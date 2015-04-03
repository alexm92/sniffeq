#!/bin/bash

sudo su -

# Install missing modules
apt-get update --fix-missing
apt-get install vim python-pip python-setuptools --assume-yes
pip install ipython==3.0

# Add PYTHONPATH to user profile
echo "export PYTHONPATH=/opt/repo" >> ~/.profile

# add HOSTS
echo "192.168.10.100 graphite.local" >> /etc/hosts
echo "192.168.10.106 mongodb.local" >> /etc/hosts

# install SniffEq
cd /opt/repo
python setup.py install

# remove SniffEq Egg
rm -rf /usr/local/lib/python2.7/dist-packages/sniffeq-*-py2.7.egg/

