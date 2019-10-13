#!/usr/bin/env python
from json_utils import *
from slackscrape import scrape_slack
from slackclient import SlackClient
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
    args = get_args()

    for idx, channel in enumerate(sorted_channels(args)):
        chan_name = channel['name'].encode('utf-8')
        print('{} | {} - {} MEMBERS'.format(idx, chan_name, channel['num_members']))
        dump_path = write_path(chan_name, args)

        try:
            old_json = load_json(dump_path)
        except Exception as e:
            old_json = []
            print('No existing messages, starting from scratch...')

        slack_args = {
            'channel': channel['id'],
            'oldest': scrape_start_time(old_json ,args['update']),
            'count': '700',
        }
        new_messages = scrape_slack(config['token'], slack_args)

        write_channel(new_messages, old_json, args['update'], dump_path)

        time.sleep(1)
