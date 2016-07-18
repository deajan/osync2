OSYNC2 - Full multimaster file synchronization tool

This is a rewrite of osync v1 in Python3 in order to handle multimaster sync scenarios.
Nothing is working yet, this is still only work in progress done in free time.

Note from 18 July 2016:
osync v1.1 RC2 is out: If no other bugs found, in a week v1.1 goes final and osync2 dev will go on.

Help is welcome :)


## Prerequisites

You need a python >= 3.2 interpreter and the watchdog >= 0.83 module
Python 3.x is needed for ctime accuracy
Python 3.2+ is needed for os.makedirs

## Installation

yum install python34
curl https://bootstrap.pypa.python3.4 > get-pip.py
python3.4 get-pip.py
pip3 install watchdog

