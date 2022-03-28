class AbstractSlackEscapeOperation:

    def __init__(self):
        self._config_json = None

    @property
    def description(self):
        raise NotImplementedError("description must be specified")

    def configure_arg_parser(self, task_name, subparsers):
        parser = subparsers.add_parser(task_name, help=self.description)
        self.configure_subparser(parser)
        parser.set_defaults(func=self.execute_task)

    def configure_subparser(self, subparser):
        raise NotImplementedError("parser must be defined")
