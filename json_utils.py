import io
import json
from operator import itemgetter
from datetime import datetime
import time
import os

def load_json(path):
    with io.open(path, encoding='utf-8') as f:
        return json.loads(f.read())

def dump_json(path, data):
    with open(path, mode='w') as f:
        json.dump(data, f, indent = 2)

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def write_path(channel_name, args, subdir='messages'):
    output = args['output'] or channel_name
    chan_path = ensure_dir('./output/channels/{}/{}/'.format(channel_name, subdir))
    return  '{}/{}.json'.format(chan_path, output)


