import csv
import json
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        pass

    def execute_task(self, args):
        old_to_new_mapping = self.get_old_to_new_users_mapping()

        with self.get_slack_export_root().joinpath('user_to_channel_name.json').open('r') as f:
            user_to_channel_mapping = json.loads(f.read())

        channel_users = defaultdict(list)
        for uid, channels in user_to_channel_mapping.items():
            user = old_to_new_mapping[uid]
            name = user['new_id']
            for channel in channels:
                channel_name = self.get_channel_new_name(channel)
                channel_users[channel_name].append(name)

        for channel, users in channel_users.items():
            for user in users:
                print(f'mmctl channel users add school:{channel} {user}')
