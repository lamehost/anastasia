#!/usr/bin/python
import os
from flask import current_app
from anastasia.configuration import get_config
from anastasia.cli import anastasia as application

# Get config file
config_file = os.environ.get('config', 'anastasia.cfg')

# Handle relative paths
if not os.path.isabs(config_file):
	basedir = os.path.dirname(os.path.realpath(__file__))
	config_file = os.path.join(basedir, config_file)

# Read config
config = get_config(config_file)

# Configure app
with application.app_context():
    current_app.config['folder'] = config['folder']
    current_app.config['client_ids'] = config['client_ids']
