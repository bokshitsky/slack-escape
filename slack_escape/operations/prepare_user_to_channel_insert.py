import csv
from collections import defaultdict

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = "convert users from exported csv to json"

    def configure_subparser(self, parser):
        parser.add_argument(dest='file', type=str, help='users to convert csv file', nargs='?')

    def execute_task(self, args):
        with open(args.file, "r") as csvfile:
            reader = csv.DictReader(csvfile)

            mapping = defaultdict(list)
            for line in reader:
                channel = self.get_channel_new_name(line["channel"])
                mapping[f'{line["team"]}:{channel}'].append(line['username'].lower())

        for team_channel, users in mapping.items():
            users_line = " ".join(users)
            print(f'mmctl channel users add {team_channel} {users_line}')
