
from collections import namedtuple
import os.path
import yaml

MachineTuple = namedtuple('MachineTuple', ['domain', 'host'])


def split_domainhost(dh):
    if ';' in dh:
        d, h = dh.split(';', 1)
    else:
        d, h = dh, dh

    return MachineTuple(d, h if h else None)


def load_default_options(module_filepath):
    filepath = os.path.dirname(module_filepath) + '/option.yaml'
    try:
        yaml_obj = yaml.load(open(filepath, 'r'))
    except:
        return {}
    if isinstance(yaml_obj, list):
        yaml_obj = dict(zip(range(len(yaml_obj)), yaml_obj))
    return yaml_obj

