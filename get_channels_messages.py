#!/usr/bin/env python
from json_utils import *
from slackscrape import scrape_slack
from slackclient import SlackClient
import argparse
import operator
import os
import pdb

config = load_json('./env.json')
oldest_time = '' # 1467331200

def sorted_channels(args):
    slack_args = {
        'exclude_archived': 0 if args.has_key('archived') and args['archived'] else 1,
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('channels.list', **slack_args)
    channels = response['channels']

    return sorted(channels, key=lambda x: x['num_members'], reverse=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--archived', help = 'include archived channels', action="store_true")
    ap.add_argument('-u', '--update', help = 'update channels', action="store_true")
    args = vars(ap.parse_args())

    for idx, channel in enumerate(sorted_channels(args)):
        chan_name = channel['name'].encode('utf-8')
        print('{} | {} - {} MEMBERS'.format(idx, chan_name, channel['num_members']))
        dump_path = write_path(chan_name, args)

        try:
            old_json = load_json(dump_path)
        except Exception as e:
            old_json = []
            print('No existing messages, starting from scratch...')

        if args['update']:
            if len(old_json): oldest_time = old_json[0]['ts']

        slack_args = {
            'channel': channel['id'],
            'oldest': oldest_time,
            'count': '700',
        }

        new_messages = scrape_slack(config['token'], slack_args)

        if len(new_messages) and args['update']:
            all_messages = new_messages + old_json
        elif not len(new_messages) and args['update']:
            all_messages = old_json
        else:
            all_messages = new_messages

        dump_json(dump_path, all_messages)
        time.sleep(1)
