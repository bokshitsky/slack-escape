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
                if 'filetype' in file_task:
                    file_location = file_location.with_suffix(file_task['filetype'])

                logging.info(f'{index} processing {file_name}, dt={file_task["x-dt"]}')
                if file_location.exists():
                    logging.info(f'file {file_name} () exists, skipping')
                    task_queue.task_done()
                    continue

                if 'url_private_download' not in file_task:
                    logging.error(f'missing download url for {file_task}')
                    task_queue.task_done()
                    continue

                timeout = aiohttp.client.ClientTimeout(15, 2)
                async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {token}'},
                                                 timeout=timeout) as session:
                    async with session.get(file_task['url_private_download']) as resp:
                        content = await resp.read()
                        with file_location.open("wb") as f:
                            f.write(content)
            except asyncio.TimeoutError:
                logging.warning(f'got timeout for file {file_name}')

            except Exception:
                logging.exception(f'{index} error on file {file_task} download')

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
