import csv
import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = "convert users from exported csv to json"

    def configure_subparser(self, parser):
        parser.add_argument(dest='file', type=str, help='users to convert csv file', nargs='?')

    def execute_task(self, args):
        with open(args.file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            with self.get_users_path().open('w') as f:
                f.write(json.dumps({line['userid']: line for line in reader}, ensure_ascii=False))

        self.get_users()
