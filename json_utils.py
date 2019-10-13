import io
import json
from operator import itemgetter
from datetime import datetime
import time
import os
import argparse

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

def write_channel(new_messages, old_json, update, dump_path):

    print( [len(new_messages),len(old_json),update] )

    if len(new_messages) and update:
        all_messages = json.dumps(new_messages) + str(old_json)
    elif not len(new_messages) and update:
        all_messages = str(old_json)
    else:
        all_messages = json.dumps(new_messages)

    with open(dump_path, "w") as text_file: text_file.write( all_messages )

def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--channel', help = 'channel id to scrape')
    ap.add_argument('-C', '--channel-name', help = 'channel name to scrape')
    ap.add_argument('-o', '--output', help = 'file to save out')
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    return vars(ap.parse_args())


