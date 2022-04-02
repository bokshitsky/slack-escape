import json
import logging
from datetime import datetime
from pathlib import Path

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'download channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-c', dest='channel', default=None, help='channel to load')
        parser.add_argument('-l', dest='limit', default=300, help='limit messages')
        parser.add_argument('-d', dest='direction', default='both', choices=('up', 'down', 'both'),
                            help='scan direction')

    def execute_task(self, args):
        logging.info(f'load channel {args.channel}')
        channel = self._get_channel(args)
        channel_root = self.get_channel_root(args.channel)
        if not channel_root.exists():
            channel_root.mkdir()

        latest, oldest = self.get_latest_and_oldest_ts(args, channel_root)

        if args.direction in ('both', 'down'):
            self.perform_messages_save(args, channel_root, channel['id'], latest, None)  # down side

        if args.direction in ('both', 'up') and oldest:
            self.perform_messages_save(args, channel_root, channel['id'], None, oldest)  # up side

    def perform_messages_save(self, args, channel_root, channel_id, latest, oldest):
        cursor, actual_latest, actual_oldest = None, None, None
        tmp_path = channel_root.joinpath('_tmp')
        client = self.get_slack_web_client(args)
        try:
            with tmp_path.open("w+") as tmp:
                for _ in range(100000):
                    response = client.conversations_history(channel=channel_id,
                                                            limit=args.limit,
                                                            cursor=cursor,
                                                            latest=latest,
                                                            oldest=oldest)

                    messages = response.get('messages')
                    if not messages:
                        break

                    if actual_latest is None:
                        actual_latest = messages[0]['ts']

                    for message in messages:
                        replies_response = None
                        if message.get('thread_ts') and message.get('reply_count'):
                            replies_response = client.conversations_replies(channel=channel_id,
                                                                            ts=message.get('thread_ts'),
                                                                            limit=500)
                        actual_oldest = message['ts']
                        message['x-dt'] = str(datetime.fromtimestamp(float(actual_oldest)))
                        json.dump(message, tmp, ensure_ascii=False)
                        tmp.write('\n')
                        if replies_response is not None:
                            for i, reply in enumerate(replies_response['messages'], 1):
                                reply['x-reply-number'] = i
                                reply['x-dt'] = str(datetime.fromtimestamp(float(message['ts'])))
                                json.dump(reply, tmp, ensure_ascii=False)
                                tmp.write('\n')
                    logging.info(
                        f'{args.channel}: processed {actual_latest}-{actual_oldest} ('
                        f'{datetime.fromtimestamp(float(actual_oldest))})'
                    )
                    if not response.data.get('has_more', False):
                        break

                    cursor = response.data['response_metadata']['next_cursor']
        except (Exception, KeyboardInterrupt):
            logging.exception('{args.channel}: error during slack export')

        if actual_latest and actual_oldest:
            new_path = channel_root.joinpath(f'{actual_latest}-{actual_oldest}.jsonl')
            logging.info(f'{args.channel}: rename {tmp_path} to {new_path}')
            tmp_path.rename(channel_root.joinpath(new_path))
        else:
            logging.info(f'{args.channel}: no messages found')
            tmp_path.unlink()

    def get_latest_and_oldest_ts(self, args, channel_root: Path):
        files = list(channel_root.glob("*.jsonl"))
        if not files:
            return None, None

        if args.direction == 'both':
            return (
                min([f.stem.split('-')[1].replace('_', '.') for f in files], key=float),
                max([f.stem.split('-')[0].replace('_', '.') for f in files], key=float)
            )
        if args.direction == 'down':
            return (
                min([f.stem.split('-')[1].replace('_', '.') for f in files], key=float),
                None
            )
        if args.direction == 'up':
            return (
                None,
                max([f.stem.split('-')[0].replace('_', '.') for f in files], key=float)
            )
        raise RuntimeError(f'not supported args {args}')

    def _get_channel(self, args):
        client = self.get_slack_web_client(args)
        channels = client.conversations_list(types='private_channel', limit=1000)['channels']

        channel = next((c for c in channels if c['name'] == args.channel), None)
        if channel:
            return channel

        channels = client.conversations_list(types='public_channel', limit=1000)['channels']
        return next((c for c in channels if c['name'] == args.channel), None)
