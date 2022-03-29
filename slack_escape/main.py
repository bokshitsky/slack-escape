import argparse
from importlib import import_module
from pkgutil import walk_packages

import slack_escape.operations


def _parse_args():
    parser = argparse.ArgumentParser(description='escape from slack to mmh')
    subparsers = parser.add_subparsers(help='sub-command help', required=True)

    for module_info in walk_packages(slack_escape.operations.__path__, slack_escape.operations.__name__ + '.'):
        file_name = module_info.name.split('.')[-1]
        import_module(module_info.name).Operation().configure_arg_parser(file_name, subparsers)

    return parser.parse_args()


def main():
    args = _parse_args()
    args.func(args)
