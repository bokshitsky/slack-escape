import csv
import json

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = "prepare users"

    def configure_subparser(self, parser):
        parser.add_argument(dest='file', type=str, help='users import csv file', nargs='?')

    def execute_task(self, args):
        print(json.dumps({
            "type": "version",
            "version": 1
        }))
        with open(args.file, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                obj = {
                    "type": "user",
                    "user": {
                        "username": line["username"],
                        "email": line["email"],
                        "auth_service": "",
                        "password": "nenene",
                        "nickname": line["displayname"],
                        "first_name": line['fullname'].split(' ')[0],
                        "last_name": "family",
                        "position": "Senior Developer",
                        "roles": "system_user",
                        "teams": [
                            {
                                "name": "hhru",
                                "roles": "team_admin team_user",
                            }
                        ]
                    }
                }

                print(json.dumps(obj))
