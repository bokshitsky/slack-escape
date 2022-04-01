import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'prepare mmctl command to insert channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-c', dest='channel', help='channel')
        parser.add_argument('-w', dest='team', help='team')
        parser.add_argument('-pr', dest='private', action='store_true', help='force private')
        parser.add_argument('-pu', dest='public', action='store_true', help='force public')

    def execute_task(self, args):
        purpose = ''
        private = ''
        header = ''
        with self.get_slack_export_root().joinpath("channels_list.jsonl").open("r") as f:
            for line in f:
                channel = json.loads(line)
                if channel['name'] != args.channel:
                    continue
                if channel['is_archived']:
                    return

                purpose_value = channel['purpose']['value']
                if purpose_value:
                    purpose = f'--purpose "{purpose_value}"'

                if not args.public and not args.private and channel['is_private']:
                    private = '--private'

                topic = channel['topic']['value']
                if topic:
                    header = f'--header "{topic}"'
                elif purpose_value:
                    header = f'--header "{purpose_value}"'
                break

        if args.private:
            private = '--private'
        elif args.public:
            private = ''

        name = self.get_channel_new_name(args.channel)
        print(
            f'mmctl channel create --team {args.team} '
            f'--name "{name}" --display-name "{args.channel}" {header} {purpose} '
            f'{private}'
        )
