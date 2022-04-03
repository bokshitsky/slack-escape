import csv
import json
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        parser.add_argument('-c', dest='channel', help='channel')
        parser.add_argument('-w', dest='team', help='team')
        parser.add_argument('-u', dest='user', help='user')

    def execute_task(self, args):
        channel_name = self.get_channel_new_name(args.channel)
        print(f'mmctl channel users add {args.team}:{channel_name} {args.user}')
