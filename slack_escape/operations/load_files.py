import asyncio
import logging

from slack_escape.operations import AbstractSlackEscapeOperation


async def worker(queue):
    while True:
        task = await queue.get()

        logging.info(f'{task}')
        await asyncio.sleep(2)
        queue.task_done()


# async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {token}'}) as session:
#     async with session.get('https://files.slack.com/files-pri/T04FNDMK1-F01U5EA7FBK/download/screenshot_from_2021
#     -04-09_11-05-32.png') as resp:
#         pass


class Operation(AbstractSlackEscapeOperation):
    description = 'download files'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-c', dest='channel', default=None, help='channel to load')

    def execute_task(self, args):
        queue = asyncio.queues.Queue()
        # queue.

        # asyncio.run(main(self.get_slack_token(args)))
# client = self.get_slack_web_client(args)
#
# channel = self._get_channel(args)
# channel_id = channel['id']
# channels_root = self.get_slack_export_root().joinpath("channels")
# if not channels_root.exists():
#     channels_root.mkdir()
#
# channel_root = channels_root.joinpath(args.channel)
# if not channel_root.exists():
#     channel_root.mkdir()
#
# latest, oldest = self.get_latest_and_oldest_ts(args, channel_root)
#
# cursor, actual_latest, actual_oldest = None, None, None
# tmp_path = channel_root.joinpath('_tmp')
#
# try:
#     with tmp_path.open("w+") as tmp:
#         for _ in range(100000):
#             response = client.conversations_history(channel=channel_id,
#                                                     limit=args.limit,
#                                                     cursor=cursor,
#                                                     latest=latest,
#                                                     oldest=oldest)
#
#             messages = response.get('messages')
#             if not messages:
#                 break
#
#             if actual_latest is None:
#                 actual_latest = messages[0]['ts']
#
#             for message in messages:
#                 replies_response = None
#                 if message.get('thread_ts') and message.get('reply_count'):
#                     replies_response = client.conversations_replies(channel=channel_id,
#                                                                     ts=message.get('thread_ts'),
#                                                                     limit=500)
#                 actual_oldest = message['ts']
#                 message['x-dt'] = str(datetime.fromtimestamp(float(actual_oldest)))
#                 json.dump(message, tmp, ensure_ascii=False)
#                 tmp.write('\n')
#                 if replies_response is not None:
#                     for i, reply in enumerate(replies_response['messages'], 1):
#                         reply['x-reply-number'] = i
#                         reply['x-dt'] = str(datetime.fromtimestamp(float(message['ts'])))
#                         json.dump(reply, tmp, ensure_ascii=False)
#                         tmp.write('\n')
#             logging.info(
#                 f'processed {actual_latest}-{actual_oldest} ({datetime.fromtimestamp(float(actual_oldest))})'
#             )
#             if not response.data.get('has_more', False):
#                 break
#
#             cursor = response.data['response_metadata']['next_cursor']
# except (RuntimeError, KeyboardInterrupt):
#     logging.exception('error during slack export')
#
# if actual_latest and actual_oldest:
#     new_path = channel_root.joinpath(f'{actual_latest}-{actual_oldest}.jsonl')
#     logging.info(f'rename {tmp_path} to {new_path}')
#     tmp_path.rename(channel_root.joinpath(new_path))
# else:
#     logging.info(f'no messages found')
