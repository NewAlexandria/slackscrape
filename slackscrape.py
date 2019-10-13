#!/usr/bin/env python
from json_utils import *
from slackclient import SlackClient
from get_channels_info import *

rate_limit_sec = 1.0  # default rate limiting, for import callers

def get_messages(sc, slack_args, messages, filter_func):
    history = sc.api_call("channels.history", **slack_args)
    last_ts = history['messages'][-1]['ts'] if ('has_more' in history and history['has_more'] == True ) else False
    hist_messages =  history['messages'] if ('messages' in history) else []
    filtered = list(filter(filter_func, hist_messages))
    all_messages = messages + filtered
    print('Fetched {} messages. {} Total now.'.format(len(filtered), len(all_messages)))

    return {
        'messages': all_messages,
        'last_ts': last_ts,
    }

def scrape_slack(token, slack_args, filter_func = lambda x: x):
    sc = SlackClient(token)
    results = get_messages(sc, slack_args, [], filter_func)

    while results['last_ts']:
        slack_args['latest'] = results['last_ts']
        results = get_messages(sc, slack_args, results['messages'], filter_func)
        time.sleep(rate_limit_sec)

    print('Done fetching messages. Found {} in total.'.format(len(results['messages'])))
    return results['messages']

def scrape_start_time(old_messages, update):
    channel_oldest_time = ''
    if update:
        channel_oldest_time = None
        if len(old_messages):
            try:
                channel_oldest_time = old_messages[0]['ts']
            except Exception as e:
                channel_oldest_time = ''
    return channel_oldest_time

def find_channel_by(key, val, return_key='name'):
    channels = all_channels_info('')
    for chan in channels:
        if chan[key] == val:
            return chan[return_key]

def get_channel_for(args):
    if args['channel_name']:
        channel_name = args['channel_name'].encode('utf-8')
        channel = find_channel_by('name', channel_name, 'id')
    else:
        channel = args['channel']
        channel_name = find_channel_by('id', channel).encode('utf-8')

    print( [channel_name, channel] )
    return {'id': channel, 'name': channel_name}


if __name__ == '__main__':
    config = load_json('./env.json')
    rate_limit_sec = 0.500
    
    args = get_args()

    channel = get_channel_for(args)
    dump_path = write_path_for(channel['name'], args)

    old_messages = load_channel(dump_path)

    slack_args = {
        'channel': channel['id'],
        'oldest': scrape_start_time(old_messages, args['update']),
        'count': '700',
    }
    new_messages = scrape_slack(config['token'], slack_args)

    write_channel(new_messages, old_messages, args['update'], dump_path)

