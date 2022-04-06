import csv
import json
import logging
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'found users with at least one message in channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-g', dest='glob', type=str, default='*', help='mmt team')

    def execute_task(self, args):
        users_by_channels = defaultdict(set)
        channels_by_users = defaultdict(set)

        external_profiles = defaultdict(dict)
        for channel_path in self.get_slack_export_root().joinpath("channels").glob(args.glob):
            logging.info(channel_path)
            for messages_path in channel_path.glob('*.jsonl'):
                with messages_path.open("r") as f:
                    for line in f:
                        message = json.loads(line)
                        if 'user' not in message:
                            continue
                        if 'user_profile' in message:
                            external_profiles[channel_path.stem][message['user']] = message['user_profile']
                        users_by_channels[channel_path.stem].add(message['user'])
                        channels_by_users[message['user']].add(channel_path.stem)

        users_by_channels_path = self.get_slack_export_root().joinpath('users_by_channels_with_messages.csv')
        with users_by_channels_path.open('w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['channel', 'user', 'username', 'email', 'status'])
            for channel, users in users_by_channels.items():
                for user_id in users:
                    writer.writerow([channel, user_id])
        logging.info(f'fill {users_by_channels_path}')

        external_users_path = self.get_slack_export_root().joinpath('users_external.csv')
        with external_users_path.open('w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['channel', 'user', 'name', 'team'])
            for channel, profiles in external_profiles.items():
                for user_id, profile in profiles.items():
                    writer.writerow([channel, user_id, profile['real_name'], profile['team']])
        logging.info(f'fill {external_users_path}')
