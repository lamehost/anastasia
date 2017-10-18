"""
Configuration directives for DiCaprio.
"""
import os
import yaml


def get_config(filename):
    """
    get_config(filename)

    Reads/Creates config file.
    Variable:
     - filename: File where to read/write the configuration

    If filenames exists: reads configuration, updates DEFAULT_CONFIG and returns result.
    Else: fills filename with DEFAULT_CONFIG and returns DEFAULT_CONFIG.
    """
    config = DEFAULT_CONFIG
    if os.path.exists(filename):
        with open(filename, 'r') as stream:
            _ = yaml.load(stream)
            config.update(_)
    else:
        try:
            with open(filename, 'w') as stream:
                yaml.dump(config, stream, default_flow_style=False)
                print 'Created configuration file: %s' % filename
        except IOError:
            raise IOError('Unable to create configuration file: %s' % filename)

    return config


DEFAULT_CONFIG = {
    'client_ids': [False],
    'folder': 'images/'
}
