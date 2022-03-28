import csv

from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = "prepare users"

    def configure_subparser(self, parser):
        parser.add_argument(dest='file', type=str, help='users import csv file', nargs='?')

    def execute_task(self, args):
        with open(args.file, "r") as csvfile:
            reader = csv.DictReader(open(args.file, "r"))
            for line in reader:
                print(line)
        # api = self.get_jira_api()
        # user = self.get_user()
        # found_issues = api.search_issues(f'(reporter = {user} or assignee = {user}) ORDER BY created DESC',
        #                                  maxResults=args.limit)
        # max_len = max(len(issue.permalink()) for issue in found_issues)
        # for issue in found_issues:
        #     print(f'{issue.permalink().ljust(max_len)} {issue.fields.summary[:80]}')
