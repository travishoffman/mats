#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# set prompt responses for mysql
apt-get update
apt-get -q -y install mongodb
apt-get -q -y install python-setuptools
apt-get -q -y install python-pip
pip install pymongo
pip install rauth
pip install mock
pip install pytz