from slack_escape.operations import AbstractSlackEscapeOperation


class Operation(AbstractSlackEscapeOperation):
    description = "12121212"

    def configure_subparser(self, parser):
        # parser.add_argument(dest='task_type', default='hh', help='task type', nargs='?',
        #                     choices=tuple(TASK_MAPPING.keys()))
        parser.add_argument('-s', dest='service', default=None,
                            help='task service - used for [{task service} prefix only')
        parser.add_argument('-p', dest='portfolio', default=None, help='[optional] portfolio to link')
        parser.add_argument('-m', dest='message', required=True, help='task name')
        parser.add_argument('-sp', dest='sp', default=None, help='task storypoints, example: 0.5')

    def execute_task(self, args):
        print('create')
