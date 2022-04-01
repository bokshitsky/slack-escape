import csv
import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        pass

    def execute_task(self, args):
        with self.get_slack_export_root().joinpath('users_mapping.csv').open('r') as csvfile:
            reader = csv.DictReader(csvfile)
            old_to_new_mapping = {line['old_id']: line for line in reader}

        with self.get_slack_export_root().joinpath('user_to_channel_name.json').open('r') as f:
            user_to_channel_mapping = json.loads(f.read())

        for uid, channels in user_to_channel_mapping.items():
            user = old_to_new_mapping[uid]
            name = user['new_id']
            for channel in channels:
                channel_name = self.get_channel_new_name(channel)
                print(f'mmctl channel users add school:{channel_name} {name}')
