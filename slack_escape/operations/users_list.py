import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'download channels list'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-l', dest='limit', default=1000, help='limit messages')

    def execute_task(self, args):
        client = self.get_slack_web_client(args)
        users = client.users_list(limit=args.limit)
        pass
        # public = client.conversations_list(types='public_channel', limit=args.limit)['channels']
        #
        # with self.get_slack_export_root().joinpath('channels_list.jsonl').open('w') as f:
        #     for channel in private:
        #         json.dump(channel, f, ensure_ascii=False)
        #         f.write('\n')
        #         print(f"{channel['name']} {channel['is_private']} {channel['is_archived']}")
        #     for channel in public:
        #         json.dump(channel, f, ensure_ascii=False)
        #         f.write('\n')
        #         print(f"{channel['name']} {channel['is_private']} {channel['is_archived']}")
