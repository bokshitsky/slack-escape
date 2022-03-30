import asyncio
import json
import logging
from asyncio import Queue
from datetime import datetime
from pathlib import Path

import aiohttp

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'download files'

    def configure_subparser(self, parser):
        self._add_token_param(parser)
        parser.add_argument('-c', dest='channel', default=None, help='channel to load')
        parser.add_argument('-cc', dest='concurrency', default=4, type=int, help='download concurrency level')

    async def file_download_worker(self, index, args, files_root: Path, task_queue: Queue):
        token = self.get_slack_token(args)
        while True:
            file_task = await task_queue.get()
            file_name = file_task['id']

            try:
                file_location = files_root.joinpath(file_name)
                logging.info(f'processing {file_name}, dt={file_task["x-dt"]}')
                if file_location.exists():
                    logging.info(f'file {file_name} () exists, skipping')
                    task_queue.task_done()
                    continue

                if 'url_private_download' not in file_task:
                    logging.error(f'missing download url for {file_task}')
                    task_queue.task_done()
                    continue

                async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {token}'}) as session:
                    async with session.get(file_task['url_private_download']) as resp:
                        content = await resp.read()
                        with file_location.open("wb") as f:
                            f.write(content)

            except RuntimeError:
                logging.exception(f'error on file {file_task} download')
                await task_queue.put(file_task)

            task_queue.task_done()

    async def main(self, args):
        queue = Queue(maxsize=10)

        channel_root = self.get_channel_root(args.channel)
        channel_files_root = self.get_channel_files_root(args, channel_root)

        for i in range(args.concurrency):
            asyncio.create_task(self.file_download_worker(i, args, channel_files_root, queue))

        files = list(channel_root.glob("*.jsonl"))
        for file in files:
            with file.open('r') as f:
                for line in f:
                    message = json.loads(line)
                    message_files = message.get('files')
                    if message_files:
                        ts = message['ts']
                        for message_file in message_files:
                            message_file['x-dt'] = datetime.fromtimestamp(float(ts))
                            await queue.put(message_file)
                logging.info(f'processed {file}')

        await queue.join()

    def get_channel_files_root(self, args, channel_root):
        if not channel_root.exists():
            raise RuntimeError(f"channel {args.channel} not found")
        files_root = channel_root.joinpath("files")
        if not files_root.exists():
            files_root.mkdir()
        return files_root

    def execute_task(self, args):
        asyncio.run(self.main(args))

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
