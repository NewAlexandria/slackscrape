#!/usr/bin/env python
from json_utils import *
from slackscrape import scrape_slack, scrape_start_time
from slackclient import SlackClient
import operator
import os
import pdb

config = load_json('./env.json')

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
        dump_path = write_path_for(chan_name, args)

        old_json = load_channel(dump_path)

        slack_args = {
            'channel': channel['id'],
            'oldest': scrape_start_time(old_json, args['update']),
            'count': '700',
        }
        new_messages = scrape_slack(config['token'], slack_args)

        write_channel(new_messages, old_json, args['update'], dump_path)

        time.sleep(1)
