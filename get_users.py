#!/usr/bin/env python
from json_utils import *
from slackclient import SlackClient
import operator
import os
import argparse

config = load_json('./env.json')

if __name__ == '__main__':
    args = get_args()

    slack_args = {
        'presence': 1
    }

    sc = SlackClient(config['token'])
    response = sc.api_call('users.list', **slack_args)
    users = response['members']

    for user in users:
        user_name = user['name']
        memb_path = ensure_dir('./output/users/members')
        user_path = '{}/{}.json'.format(memb_path, user_name)

        try:
            old_json = load_json(user_path)
            if not args['update']:
                print('Aready have user {}, skipping...'.format(user_name))
                continue
        except Exception as e:
            old_json = {}
            print('No existing messages, starting from scratch...')

        print('ADDING ', user_name)

        dump_json(user_path, user)
