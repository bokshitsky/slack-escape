import json
import logging

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)

    def execute_task(self, args):
        users = self.get_users()
        found = set()
        bot_found = set()
        for channel_path in self.get_slack_export_root().joinpath("channels").glob('*'):
            logging.info(channel_path)
            for messages_path in channel_path.glob('*.jsonl'):
                with messages_path.open("r") as f:
                    for line in f:
                        message = json.loads(line)
                        if 'user' in message:
                            found.add(message['user'])
                        elif 'bot_id' in message:
                            bot_found.add(message['bot_id'])
