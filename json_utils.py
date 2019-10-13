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

def write_path_for(channel_name, args, subdir='messages'):
    output = args['output'] or channel_name
    chan_path = ensure_dir('./output/channels/{}/{}/'.format(channel_name, subdir))
    return  '{}/{}.json'.format(chan_path, output)

def load_channel(dump_path):
    try:
        old_messages = load_json(dump_path)
    except Exception as e:
        dump_path_is = os.path.isfile(dump_path)
        if dump_path_is:
            with open(dump_path, 'r') as myfile: old_messages = myfile.read()
            print('Existing messages, but there was a problem parsing. Using raw file.')
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            old_messages = []
    print( [len(old_messages),len(str(old_messages))] )
    return old_messages

def write_channel(new_messages, old_messages, update, dump_path):

    print( [len(new_messages),len(old_messages),update] )

    if len(new_messages) and update:
        all_messages = json.dumps(new_messages) + str(old_messages)
    elif not len(new_messages) and update:
        all_messages = str(old_messages)
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


