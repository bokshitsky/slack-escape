import json
import logging

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        # parser.add_argument('-c', dest='channel', help='channel')
        # parser.add_argument('-w', dest='team', help='team')
        # parser.add_argument('-pr', dest='private', action='store_true', help='force private')
        # parser.add_argument('-pu', dest='public', action='store_true', help='force public')

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

        print(len(users))
        print(len(list(u for u in users if u in found)))
