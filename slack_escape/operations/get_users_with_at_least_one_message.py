import csv
import json
import logging
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'found users with at least one message in channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)

    def execute_task(self, args):
        users_by_channels = defaultdict(set)
        channels_by_users = defaultdict(set)

        for channel_path in self.get_slack_export_root().joinpath("channels").glob('*'):
            logging.info(channel_path)
            for messages_path in channel_path.glob('*.jsonl'):
                with messages_path.open("r") as f:
                    for line in f:
                        message = json.loads(line)
                        if 'user' not in message:
                            continue
                        users_by_channels[channel_path.stem].add(message['user'])
                        channels_by_users[message['user']].add(channel_path.stem)

        with self.get_slack_export_root().joinpath('users_by_channels_with_messages.csv').open('w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['channel', 'user', 'username', 'email', 'status'])
            for channel, users in users_by_channels.items():
                for user_id in users:
                    if not user_id in self.get_users():
                        logging.warning(f"skipping {user_id}")
                        continue
                    user = self.get_users()[user_id]
                    writer.writerow([channel, user_id, user['username'], user['email'], user['status']])

        with self.get_slack_export_root().joinpath('channels_by_users_with_messages.csv').open('w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['user', 'channel', 'username', 'email', 'status'])
            for user_id, channels in channels_by_users.items():
                if not user_id in self.get_users():
                    logging.warning(f"skipping {user_id}")
                    continue
                user = self.get_users()[user_id]
                for channel in channels:
                    writer.writerow([user_id, channel, user['username'], user['email'], user['status']])
