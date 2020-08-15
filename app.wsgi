#! /usr/bin/python

import sys
sys.path.insert(0, "/var/www/clustering")
sys.path.insert(0, "/opt/conda/lib/python3.6/site-packages")
sys.path.insert(0, "/opt/conda/bin/")

import os
os.environ['PYTHONPATH'] = '/opt/conda/bin/python'

from app import app as application