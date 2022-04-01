import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'download channels list and user-to-channel mapping'

    def configure_subparser(self, parser):
        self._add_token_param(parser)

    def execute_task(self, args):
        channels_list_path = self.get_slack_export_root().joinpath('channels_list.jsonl')
        with channels_list_path.open('r') as f:
            for line in f:
                channel = json.loads(line)
                if not channel['is_archived']:
                    print(channel['name'])
