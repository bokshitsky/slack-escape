import csv
import json
import logging
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'download channels list and user-to-channel mapping'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-l', dest='limit', default=1000, help='limit messages')

    def execute_task(self, args):
        client = self.get_slack_web_client(args)
        private = client.conversations_list(types='private_channel', limit=args.limit)['channels']
        public = client.conversations_list(types='public_channel', limit=args.limit)['channels']
        all_channels = private + public

        user_channel_names = defaultdict(list)
        user_channel_ids = defaultdict(list)
        for channel in all_channels:
            logging.info(f'processing channel {channel["name"]} ({channel["id"]})')
            members = client.conversations_members(channel=channel['id'], limit=args.limit)['members']
            channel['x-members'] = members
            if not (channel['is_archived']):
                for member in members:
                    user_channel_ids[member].append(channel['id'])
                    user_channel_names[member].append(channel['name'])

        channels_list_path = self.get_slack_export_root().joinpath('channels_list.jsonl')
        with channels_list_path.open('w') as f:
            for channel in all_channels:
                json.dump(channel, f, ensure_ascii=False)
                f.write('\n')
        logging.info(f'filled {channels_list_path}')

        user_to_channel_name_path = self.get_slack_export_root().joinpath('user_to_channel_name.json')
        with user_to_channel_name_path.open('w') as f:
            json.dump(user_channel_names, f, ensure_ascii=False)
        logging.info(f'filled {user_to_channel_name_path}')

        user_to_channel_id_path = self.get_slack_export_root().joinpath('user_to_channel_id.json')
        with user_to_channel_id_path.open('w') as f:
            json.dump(user_channel_ids, f, ensure_ascii=False)
        logging.info(f'filled {user_to_channel_id_path}')

        with self.get_slack_export_root().joinpath('user_channels_current_presense.csv').open('w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['user', 'channel', 'username', 'email', 'status'])
            for user_id, channels in user_channel_names.items():
                for channel in channels:
                    user = self.get_users()[user_id]
                    writer.writerow([user_id, channel, user['username'], user['email'], user['status']])
        logging.info(f'filled {self.get_slack_export_root().joinpath("user_channels_current_presense.csv")}')
