#!/usr/bin/env python
from json_utils import *
from slackclient import SlackClient
from get_channels_info import *

rate_limit_sec = 1.0  # default rate limiting, for import callers
oldest_time = '' # 1467331200
channel_oldest_time = None

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

def find_channel_by(key, val, return_key='name'):
    channels = all_channels_info('')
    for chan in channels:
        if chan[key] == val:
            return chan[return_key]

if __name__ == '__main__':
    config = load_json('./env.json')
    rate_limit_sec = 0.500
    
    args = get_args()

    if args['channel_name']:
        channel_name = args['channel_name'].encode('utf-8')
        channel = find_channel_by('name', channel_name, 'id')
    else:
        channel = args['channel']
        channel_name = find_channel_by('id', channel).encode('utf-8')

    print( [channel_name, channel] )

    dump_path = write_path(channel_name, args)

    try:
        old_json = load_json(dump_path)
    except Exception as e:
        dump_path_is = os.path.isfile(dump_path)
        if dump_path_is:
            with open(dump_path, 'r') as myfile: old_json = myfile.read()
            print('Existing messages, but there was a problem parsing. Using raw file.')
        else:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            old_json = []
    print( [len(old_json),len(str(old_json))] )

    if args['update']:
        channel_oldest_time = None
        if len(old_json):
            try:
                channel_oldest_time = old_json[0]['ts']
            except Exception as e:
                channel_oldest_time = ''

    slack_args = {
        'channel': channel,
        'oldest': channel_oldest_time if channel_oldest_time else oldest_time,
        'count': '700',
    }
    new_messages = scrape_slack(config['token'], slack_args)

    write_channel(new_messages, old_json, args['update'], dump_path)

