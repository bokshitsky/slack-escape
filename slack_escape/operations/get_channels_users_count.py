import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)

    def execute_task(self, args):
        with self.get_slack_export_root().joinpath("channels_list.jsonl").open("r") as f:
            for line in f:
                channel = json.loads(line)
                # len(self.get_slack_web_client(args).conversations_history(limit=1000)['messages'])
                try:
                    print(channel['name'], ",", len(channel['x-members']), ",", len(self.get_slack_web_client(args).conversations_history(channel=channel['id'], limit=20)['messages']))
                except Exception:
                    pass
