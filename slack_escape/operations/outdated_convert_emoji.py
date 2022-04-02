import json
import logging
from pathlib import Path

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'emoji upload'

    def configure_subparser(self, parser):
        parser.add_argument('-d', dest='dir', help='folder with emoji')

    def execute_task(self, args):
        print('{"type": "version", "version": 1}')
        for emoji_file in Path(args.dir).glob('*'):
            print(json.dumps({
                "type": "emoji",
                "emoji": {
                    "name": self.to_latin(emoji_file.stem),
                    "image": "slack-emoji/" + emoji_file.name
                }
            }, ensure_ascii=False))
