import csv
import json
import logging
import os
import pathlib
import sys
from logging import root
from typing import Optional

import cyrtranslit
from slack_sdk import WebClient
from slack_sdk.http_retry import RetryHandler, RetryState, HttpRequest, HttpResponse
from slack_sdk.http_retry.builtin_interval_calculators import BackoffRetryIntervalCalculator

root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class AbstractSlackEscapeOperation:

    def __init__(self):
        self.__slack_web_client = None
        self.__slack_export_root = None
        self.__old_to_new_users_mapping = None
        self.__users = None

    @property
    def description(self):
        raise NotImplementedError('description must be specified')

    def configure_arg_parser(self, task_name, subparsers):
        parser = subparsers.add_parser(task_name, help=self.description)
        self.configure_subparser(parser)
        parser.set_defaults(func=self.execute_task)

    def configure_subparser(self, subparser):
        raise NotImplementedError('parser must be defined')

    def get_slack_export_root(self):
        if not self.__slack_export_root:
            env_var_path = os.environ.get('SLACK_EXPORT_ROOT_PATH')
            if env_var_path:
                path = pathlib.Path(env_var_path)
            else:
                path = pathlib.Path.home().joinpath('slack_export')

            if not path.exists():
                path.mkdir()
            self.__slack_export_root = path
        return self.__slack_export_root

    def get_channel_root(self, channel_name: str) -> pathlib.Path:
        channels_root = self.get_slack_export_root().joinpath("channels")
        if not channels_root.exists():
            channels_root.mkdir()
        return channels_root.joinpath(channel_name)

    def _add_token_param(self, parser):
        parser.add_argument('-t', dest='token', default=None,
                            help='[optional] slack user token. "SLACK_EXPORT_ROOT_PATH" env var is used if omitted')

    def get_slack_web_client(self, args):
        if not self.__slack_web_client:
            self.__slack_web_client = WebClient(
                token=self.get_slack_token(args),
                retry_handlers=[AlwaysRetryHandler(
                    max_retry_count=20,
                    interval_calculator=BackoffRetryIntervalCalculator(
                        backoff_factor=1.0,
                    )
                )]
            )
        return self.__slack_web_client

    def get_slack_token(self, args):
        return args.token if args.token else os.environ['SLACK_USER_TOKEN']

    def get_users_path(self):
        return self.get_slack_export_root().joinpath('users.json')

    def get_users(self):
        if self.__users is None:
            with self.get_users_path().open('r') as f:
                self.__users = json.load(f)
        return self.__users

    def get_channel_new_name(self, old_name):
        return self.to_latin(old_name)

    def to_latin(self, old_name):
        return cyrtranslit.to_latin(old_name, 'ru').replace("'", '')

    def get_old_to_new_users_mapping(self):
        if self.__old_to_new_users_mapping is None:
            with self.get_slack_export_root().joinpath('users_mapping.csv').open('r') as csvfile:
                reader = csv.DictReader(csvfile)
                self.__old_to_new_users_mapping = {line['old_id']: line for line in reader}
        return self.__old_to_new_users_mapping


class AlwaysRetryHandler(RetryHandler):

    def _can_retry(self, *, state: RetryState, request: HttpRequest, response: Optional[HttpResponse] = None,
                   error: Optional[Exception] = None) -> bool:
        logging.warning(f'perform retry {state.current_attempt} data={request.data} ')
        return True
