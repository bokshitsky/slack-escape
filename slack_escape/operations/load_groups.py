import csv
import json
import logging
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = 'found users with at least one message in channel'

    def configure_subparser(self, parser):
        self._add_token_param(parser)

    def execute_task(self, args):
        client = self.get_slack_web_client(args)
        resp = client.usergroups_list(include_disabled=False,include_users=True)
        with self.get_slack_export_root().joinpath("user_groups.json").open("w") as file:
            file.write(json.dumps(resp['usergroups']))
        pass
